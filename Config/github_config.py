from pydantic import Field
from pydantic.v1 import BaseSettings


class GitHubConfig(BaseSettings):
    github_username: str = Field(..., env="GITHUB_USERNAME")
    github_repo: str = Field(..., env="GITHUB_REPO")
    github_token: str = Field(..., env="GITHUB_TOKEN")
    github_branch: str = Field(default="main", env="GITHUB_BRANCH")

    class Config:
        env_file = ".env"
