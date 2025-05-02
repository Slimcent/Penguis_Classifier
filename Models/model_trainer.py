import pandas as pd
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
from Services.logger_service import LoggerService
from Dtos.Response.model_response import ModelInfoResponse, TrainingInfo, DataInfo


class ModelTrainer:
    def __init__(self):
        self.logger = LoggerService("training_logger").get_logger()
        self.label_encoder = LabelEncoder()
        self.model = None
        self.data_info = None
        self.training_info = None

    async def train_model(self) -> ModelInfoResponse:
        raw_data = pd.read_csv('penguins.csv')
        initial_rows = len(raw_data)
        data = raw_data.dropna()
        cleaned_rows = len(data)
        dropped_rows = initial_rows - cleaned_rows

        X = data[["bill_length_mm", "flipper_length_mm"]]
        self.label_encoder.fit(data["species"])
        y = self.label_encoder.transform(data["species"])

        X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=0)

        clf = Pipeline([
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier(n_neighbors=11))
        ])
        clf.fit(X_train, y_train)
        self.model = clf

        train_accuracy = accuracy_score(y_train, clf.predict(X_train))
        test_accuracy = accuracy_score(y_test, clf.predict(X_test))

        label_mapping = {i: species for i, species in enumerate(self.label_encoder.classes_)}

        self.data_info = DataInfo(
            initial_rows=initial_rows,
            cleaned_rows=cleaned_rows,
            dropped_rows=dropped_rows
        )

        self.training_info = TrainingInfo(
            train_accuracy=round(train_accuracy, 3),
            test_accuracy=round(test_accuracy, 3),
            label_mapping=label_mapping
        )

        summary = f"""
        Model Training Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        -------------------------------------------------
        Rows loaded      : {initial_rows}
        Rows after clean : {cleaned_rows}
        Rows dropped     : {dropped_rows}
        Train Accuracy   : {round(train_accuracy, 3)}
        Test Accuracy    : {round(test_accuracy, 3)}
        Label Mapping    : {label_mapping}
        -------------------------------------------------
        """
        self.logger.info("Model training completed.")
        self.logger.info(summary.strip())

        return ModelInfoResponse(
            name="Penguins Prediction",
            description="Predict penguin species based on bill length and flipper length.",
            data_info=self.data_info,
            training_info=self.training_info
        )

    def get_model(self):
        return self.model

    def get_label_encoder(self):
        return self.label_encoder
