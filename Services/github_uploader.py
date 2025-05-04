import io
import csv
import httpx
import base64
import pandas as pd
from Config.github_config import GitHubConfig
from typing import Optional, Tuple, List, Dict
from Services.logger_service import LoggerService


class GitHubUploader:
    def __init__(self):
        config = GitHubConfig()
        self.github_username = config.github_username
        self.github_repo = config.github_repo
        self.github_token = config.github_token
        self.github_branch = config.github_branch
        self.http_client = httpx.AsyncClient()
        self.logger = LoggerService("github_uploader_service").get_logger()

        self.logger.info("GitHubUploader initialized with config:")
        self.logger.info(f"Username: {self.github_username}")
        self.logger.info(f"Repository: {self.github_repo}")
        self.logger.info(f"Branch: {self.github_branch}")

    def build_url(self, path: str) -> str:
        url = f"https://api.github.com/repos/{self.github_username}/{self.github_repo}/contents/{path}"
        self.logger.debug(f"URL built for path '{path}': {url}")
        return url

    def build_headers(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.logger.debug(f"Headers built: {headers}")
        return headers

    def encode_content(self, content: str, is_binary: bool) -> str:
        if is_binary:
            self.logger.debug("Binary content will be used directly.")
            return content
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        self.logger.debug(f"Encoded content preview: {encoded[:100]}...")
        return encoded

    def build_payload(self, path: str, encoded_content: str, sha: Optional[str]) -> dict:
        payload = {
            "message": f"{'Update' if sha else 'Create'} prediction file: {path}",
            "content": encoded_content,
            "branch": self.github_branch
        }
        if sha:
            payload["sha"] = sha
        self.logger.debug(f"Payload built for '{path}': {str(payload)[:300]}...")
        return payload

    async def get_github_file_sha(self, path: str) -> Optional[str]:
        url = self.build_url(path)
        headers = self.build_headers()
        self.logger.info(f"Checking existing SHA for: {path}")
        response = await self.http_client.get(url, headers=headers)
        self.logger.debug(f"SHA check response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            sha = response.json().get("sha")
            self.logger.info(f"Found existing SHA: {sha}")
            return sha
        elif response.status_code == 404:
            self.logger.info("No existing file found (404)")
            return None
        else:
            self.logger.error(f"Error fetching SHA: {response.text}")
            raise Exception(f"Failed to check file: {response.text}")

    async def upload_file_to_github(self, path: str, content: str, is_binary: bool, sha: Optional[str]) \
            -> Tuple[bool, str]:

        url = self.build_url(path)
        headers = self.build_headers()
        encoded_content = self.encode_content(content, is_binary)
        payload = self.build_payload(path, encoded_content, sha)

        self.logger.info(f"Uploading file to GitHub: {path} (URL: {url})")
        response = await self.http_client.put(url, headers=headers, json=payload)

        success = response.status_code in [200, 201]
        self.logger.info(f"Upload status: {response.status_code}")
        self.logger.debug(f"Response body: {response.text}")
        return success, response.text

    async def upload_to_github(self, path: str, content: str, is_binary: bool) -> bool:
        self.logger.info(f"Starting upload process for: {path}")
        try:
            sha = await self.get_github_file_sha(path)
            success, response = await self.upload_file_to_github(path, content, is_binary, sha)
            if success:
                self.logger.info(f"Upload successful: {path}")
            else:
                self.logger.error(f"Upload failed: {response}")
            return success
        except Exception as ex:
            self.logger.exception(f"Exception during upload: {ex}")
            return False

    async def get_existing_github_file_content(self, path: str) -> List[Dict]:
        print("getting existing github data")
        try:
            url = self.build_url(path)

            headers = self.build_headers()

            async with httpx.AsyncClient() as client:
                print("getting response")
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    print("got response")
                    file_info = response.json()
                    file_content = base64.b64decode(file_info["content"]).decode("utf-8")

                    # Determine if the file is CSV or Excel by its path extension
                    if path.endswith(".csv"):
                        # Parse CSV content
                        print("csv response")
                        csv_reader = csv.DictReader(io.StringIO(file_content))
                        existing_rows = [row for row in csv_reader]
                    elif path.endswith(".xlsx"):
                        # Parse Excel content
                        print("excel response")
                        excel_buffer = io.BytesIO(file_content.encode("utf-8"))
                        df = pd.read_excel(excel_buffer)
                        existing_rows = df.to_dict(orient="records")
                    else:
                        existing_rows = []

                    return existing_rows
                else:
                    self.logger.error(f"Failed to retrieve file from GitHub: {response.text}")
                    return []

        except Exception as e:
            self.logger.error(f"Error retrieving GitHub file content: {e}")
            return []
