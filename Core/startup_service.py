from Models.model_trainer import ModelTrainer


class StartupService:
    async def run(self):
        trainer = ModelTrainer()
        await trainer.train_model()
