from fastapi import FastAPI
from Controllers import predict_controller, model_info_controller
from Core.startup_service import StartupService
from Core.global_model_loader import model_loader


def create_app() -> FastAPI:
    app = FastAPI(
        title="Penguin Species Prediction API",
        description="API to predict penguin species based on features.",
        version="1.0.0"
    )

    # Register routers
    app.include_router(model_info_controller.router, prefix="/api/info", tags=["Overview"])
    app.include_router(predict_controller.router, prefix="/api/predict", tags=["Prediction"])

    # Trigger startup logic (like training model)
    @app.on_event("startup")
    async def on_startup():
        startup_service = StartupService()
        await startup_service.run()

    @app.on_event("startup")
    async def load_model_on_startup():
        await model_loader.load_model()

    return app
