# Penguin Species Prediction API

🐧 Overview
The Penguin Species Prediction API is designed to predict the species of penguins based on biometric data using the K-Nearest Neighbors (KNN) algorithm. This API offers several endpoints for individual predictions, batch processing, and file-based predictions, with seamless integration to GitHub for saving and retrieving data. 
The system also provides an efficient caching mechanism to avoid retraining the model on every API call, ensuring high performance.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)](https://fastapi.tiangolo.com/)


---

## 📑 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [API Usage](#api-usage)
- [GitHub Integration](#github-integration)
- [Prediction Model](#prediction-model)
- [Folder Structure](#folder-structure)
- [License](#license)

---

 ##  Features

### 🔍 K-Nearest Neighbors Classifier
- Predicts penguin species using features like flipper length, bill depth, and more.
- Simple yet effective algorithm for high accuracy.

### ⚡ Model Caching
- Model is cached in memory after training.
- Eliminates retraining on every API call for faster responses.

### 📂 File Upload Support
- Accepts both `.csv` and `.xlsx` formats.
- Enables easy bulk prediction via spreadsheet uploads.

### 📥 Downloadable Output
- Returns processed Excel files with added prediction results.

### ⚙️ FastAPI Framework
- Built with **FastAPI** for high-speed, asynchronous request handling.
- Auto-generates Swagger UI for interactive API exploration.

### 🔁 Duplicate Handling
- Avoids duplicate entries during saving to local directory and uploads to GitHub.

### 🌐 Local and GitHub Storage
- Saves predictions locally and pushes them to a connected GitHub repo.

### 📖 Documentation and OpenAPI
- Interactive, auto-generated documentation using Swagger UI.
- Easily test endpoints and explore request/response formats.

### 🧱 Error Handling and Logging
- Includes robust error messages and log tracking.
- Helps in quick debugging and maintaining API stability.

### 🧵 Asynchronous Operations
- Fully async design supports high-concurrency use cases.

### 🧩 API Endpoints

- `GET /model-info`  
  View model metadata (accuracy, parameters, training status).


- `POST /predict-single`  
  Submit a single penguin record and get a predicted species.


- `POST /predict-batch` 
  Send multiple records in JSON format for bulk predictions.


- `POST /predict-from-file`  
  Upload `.csv` or `.xlsx` files and receive species predictions for each entry.


- `POST /download-predictions`  
  Upload a file and download a new Excel file with prediction results appended.

---
## Tech Stack

- **Python 3.10+**
- **FastAPI**
- **Scikit-learn**
- **Pandas / NumPy**
- **Uvicorn**
- **GitHub API (for file storage)**
- **OpenPyXL / xlrd** (for Excel support)

---

## Installation
Follow the steps below to set up and run the Penguin Species Prediction API locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Slimcent/Penguis_Classifier.git

```

### 2. Create and Activate a Virtual Environment
```bash
pip install python-dotenvpython -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Set Up Environment Variables
- Create a .env file in the root directory.
- Install the python-dotenv package:

```bash
pip install python-dotenv
```

- Add your GitHub token and repository information
- Create your GitHub access token from here

```bash
https://github.com/settings/personal-access-tokens/
```
- Put your GitHub access token and repository information in the .env file like this;

```bash
# .env template
GITHUB_TOKEN=your_personal_access_token
GITHUB_REPO=your-username/your-repo-name
```
- Make sure to ignore the .env file by adding it to your .gitignore.

```bash
# .gitignore
.env
```

### 4. Run the API Server
```bash
uvicorn app.main:app --reload
```
- The API will be available at:

```bash
http://127.0.0.1:8000
```

- API documentation can be accessed at:
```bash
http://127.0.0.1:8000/docs
```

---


## API Usage

### 🔍 `GET /model-info`
Retrieve metadata about the trained model.

**Response:**
```json
{
  "success": true,
  "message": "string",
  "data": {
    "name": "string",
    "description": "string",
    "data_info": {
      "initial_rows": 0,
      "cleaned_rows": 0,
      "dropped_rows": 0
    },
    "training_info": {
      "train_accuracy": 0,
      "test_accuracy": 0,
      "label_mapping": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
      }
    }
  }
}

```

🐧 POST `/predict-single`  
Predict the species of a single penguin.
**Request Body:**
```json
{
  "bill_length_mm": 39.1,
  "flipper_length_mm": 210.5
}
```
**Response:**
```json
{
  "success": true,
  "message": "string",
  "data": {
    "prediction": "string",
    "probabilities": {
      "additionalProp1": 0,
      "additionalProp2": 0,
      "additionalProp3": 0
    }
  }
}
```

📦 POST `/predict-batch`
Predict species for a batch of penguin records.
**Request Body:**
```json
{
  "records": [
    {
      "bill_length_mm": 27.1,
      "flipper_length_mm": 186.0
    },
    {
      "bill_length_mm": 40.5,
      "flipper_length_mm": 172.0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Batch prediction successful",
  "data": {
    "results": [
      {
        "prediction": "Adelie",
        "probabilities": {
          "Adelie": 1,
          "Chinstrap": 0,
          "Gentoo": 0
        }
      },
      {
        "prediction": "Adelie",
        "probabilities": {
          "Adelie": 0.91,
          "Chinstrap": 0.09,
          "Gentoo": 0
        }
      }
    ]
  }
}
```

📁 POST `/predict-from-file`
Upload a .csv or .xlsx file and receive predictions as a JSON array.

**Request:**
Upload the file using multipart/form-data with the key file.

**Response:**
```json
{
  "success": true,
  "message": "Batch prediction successful",
  "data": {
    "results": [
      {
        "prediction": "Adelie",
        "probabilities": {
          "Adelie": 1,
          "Chinstrap": 0,
          "Gentoo": 0
        }
      },
      {
        "prediction": "Adelie",
        "probabilities": {
          "Adelie": 0.91,
          "Chinstrap": 0.09,
          "Gentoo": 0
        }
      }
    ]
  }
}
```

📄 POST `/download-predictions`
Upload a .csv or .xlsx file and receive a downloadable Excel file with predictions appended.

**Request:**
Upload the file using multipart/form-data with the key file.

**Response:**
A downloadable .xlsx file with a new column: predicted_species.

✅ Notes
All responses are in `application/json` format unless otherwise specified.

Input fields should match the values used during training.

Ensure all input data has required features: `bill_length_mm` and `flipper_length_mm`.

---

## GitHub Integration

This project supports seamless integration with GitHub for automatic storage of prediction results. Each new prediction 
file generated by the API can be pushed to a specified GitHub repository, helping to maintain version-controlled 
historical records.

---

## 📁 What Gets Uploaded?

- `.xlsx` files generated via the `/predict-single`, `/predict-batch`, `/predict-from-file` and 
`/download-predictions` endpoints.
- Stored in the `/PredictionStorage` directory locally before upload.
- Each file is timestamped to avoid overwriting.

---

## 🔐 GitHub Authentication

The integration uses a **Personal Access Token (PAT)** to authenticate with the GitHub API. This token must have `repo` scope to enable uploading files.

---

## ⚙️ Setup Instructions

### 1. Create a Personal Access Token

1. Go to [GitHub Developer Settings](https://github.com/settings/tokens)
2. Click **"Generate new token"**
3. Select the **`repo`** scope
4. Click **Generate token**
5. Copy and save the token (you won’t see it again)

---

### 2. Add to `.env` File

Create a `.env` file in your project root if it does not exist, and add:

```env
GITHUB_TOKEN=your_personal_access_token
GITHUB_REPO=your-username/your-repo-name
```

---

## License
```sql
MIT License

Copyright (c) 2025, Achara Obinna Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell     
copies of the Software, and to permit persons to whom the Software is         
furnished to do so, subject to the following conditions:                      

The above copyright notice and this permission notice shall be included in    
all copies or substantial portions of the Software.                           

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR    
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,      
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE   
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER        
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN     
THE SOFTWARE.

```

---