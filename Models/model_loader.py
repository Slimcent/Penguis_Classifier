import asyncio
from Dtos.Response.model_response import ModelInfoResponse
from Models.model_trainer import ModelTrainer


class ModelLoader:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.info_response = None
        self._loading_lock = asyncio.Lock()
        self._is_loaded = False

    async def load_model(self) -> ModelInfoResponse:
        async with self._loading_lock:
            if self._is_loaded:
                return self.info_response

            trainer = ModelTrainer()
            self.info_response = await trainer.train_model()
            self.model = trainer.get_model()
            self.label_encoder = trainer.get_label_encoder()
            self._is_loaded = True

            print("Model trained and cached")
            return self.info_response

    def get_model(self):
        return self.model

    def get_label_encoder(self):
        return self.label_encoder

    def get_info_response(self):
        return self.info_response

    def is_loaded(self):
        return self._is_loaded
