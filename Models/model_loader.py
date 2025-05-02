from Models.model_trainer import ModelTrainer


class ModelLoader:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.info_response = None

    async def load_model(self):
        trainer = ModelTrainer()
        self.info_response = await trainer.train_model()
        self.model = trainer.get_model()
        self.label_encoder = trainer.get_label_encoder()
        return self

    def get_model(self):
        return self.model

    def get_label_encoder(self):
        return self.label_encoder

    def get_info_response(self):
        return self.info_response
