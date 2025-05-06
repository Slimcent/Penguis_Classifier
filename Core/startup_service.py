import os
from Models.model_trainer import ModelTrainer


class StartupService:
    async def run(self):
        trainer = ModelTrainer()
        await trainer.train_model()

    current_env = os.getenv("ENV", "prod")  # default to "prod"
    if current_env == "dev":
        print("Running in development mode.")
    else:
        print("Running in production.")
