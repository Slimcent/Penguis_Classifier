import logging
import pandas as pd
from fastapi import FastAPI
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from logging.handlers import TimedRotatingFileHandler
from Dtos.Request.penguin_input_request import PenguinInputRequest, BatchInputRequest
from sklearn.preprocessing import LabelEncoder, StandardScaler


# Set up FastAPI app
app = FastAPI()

# Set up a logger for training summary with daily log rotation
logger = logging.getLogger("training_logger")
logger.setLevel(logging.INFO)

# Create a handler that rotates logs daily at midnight
handler = TimedRotatingFileHandler("training_log.txt", when="midnight", interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d"  # Log file name becomes training_log.txt.2025-04-30 etc.

# Log formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Avoid duplicate logs if the script is re-run
if not logger.handlers:
    logger.addHandler(handler)

# Load and clean data
raw_data = pd.read_csv('penguins.csv')
initial_rows = len(raw_data)
data = raw_data.dropna()
cleaned_rows = len(data)
dropped_rows = initial_rows - cleaned_rows

# Prepare features and target
X = data[["bill_length_mm", "flipper_length_mm"]]
le = LabelEncoder()
le.fit(data["species"])
y = le.transform(data["species"])
label_mapping = dict(zip(le.transform(le.classes_), le.classes_))

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=0)

# Train model
clf = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=11))
])
clf.fit(X_train, y_train)
print("Model training completed successfully!")

# Evaluate
train_accuracy = accuracy_score(y_train, clf.predict(X_train))
test_accuracy = accuracy_score(y_test, clf.predict(X_test))

# Prepare training summary
training_summary = f"""
Model Training Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-------------------------------------------------
Model training completed successfully!
Rows loaded      : {initial_rows}
Rows after clean : {cleaned_rows}
Rows dropped     : {dropped_rows}
Train Accuracy   : {round(train_accuracy, 3)}
Test Accuracy    : {round(test_accuracy, 3)}
Label Mapping    : {label_mapping}
-------------------------------------------------
"""

# Print training summary
print("\nModel Training Summary")
print("------------------------------")
print(f"Model training completed successfully!")
print(f"Rows loaded      : {initial_rows}")
print(f"Rows after clean : {cleaned_rows}")
print(f"Rows dropped     : {dropped_rows}")
print(f"Train Accuracy   : {round(train_accuracy, 3)}")
print(f"Test Accuracy    : {round(test_accuracy, 3)}")
print(f"Label Mapping    : {label_mapping}")
print("------------------------------\n")

# Log the training summary
logger.info("Model training started.")
logger.info(training_summary)

# API metadata
data_info = {
    "initial_rows": int(initial_rows),
    "cleaned_rows": int(cleaned_rows),
    "dropped_rows": int(dropped_rows)
}

label_mapping = {i: species for i, species in enumerate(le.classes_)}

training_info = {
    "train_accuracy": float(round(train_accuracy, 3)),
    "test_accuracy": float(round(test_accuracy, 3)),
    "label_mapping": label_mapping
}


@app.get("/penguin-info", summary="Penguin Model Info", description="Returns details about the training and model.",
         tags=["Overview"])
async def root():
    return {
        "name": "Penguins Prediction",
        "description": "Predict penguin species based on bill length and flipper length.",
        "data_info": data_info,
        "training_info": training_info
    }


@app.post("/predict", summary="Predict Penguin Species", tags=["Prediction"])
async def predict_penguin(request: PenguinInputRequest):
    X_new = [[request.bill_length_mm, request.flipper_length_mm]]
    prediction = clf.predict(X_new)[0]
    proba = clf.predict_proba(X_new)[0]

    probabilities = {
        label_mapping[i]: round(float(prob), 4)
        for i, prob in enumerate(proba)
    }

    predicted_species = label_mapping[prediction]
    logger.info(f"Prediction made: {predicted_species} with probabilities {probabilities}")

    return {
        "prediction": predicted_species,
        "probabilities": probabilities
    }


@app.post("/predict-multiple", summary="Predict multiple Penguin Species", tags=["Prediction"])
async def predict_multiple(batch: BatchInputRequest):
    # Convert list of PenguinFeatures to DataFrame
    df = pd.DataFrame([record.dict() for record in batch.records])

    # Predict
    preds = clf.predict(df)
    probs = clf.predict_proba(df)

    # Map back to species labels
    results = []
    for pred, prob in zip(preds, probs):
        species = le.inverse_transform([pred])[0]
        prob_dict = {
            le.inverse_transform([i])[0]: round(p, 2)
            for i, p in enumerate(prob)
        }
        results.append({
            "prediction": species,
            "probabilities": prob_dict
        })

    return {"results": results}
