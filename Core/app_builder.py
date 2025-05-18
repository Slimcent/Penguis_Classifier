from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from Core.startup_service import StartupService
from Core.global_model_loader import model_loader
from Controllers import predict_controller, model_info_controller


def create_app() -> FastAPI:
    app = FastAPI(
        description="API to predict penguin species based on features.",
        version="1.0.0",
        # docs_url=None  # Disable default Swagger UI
    )

    # app = FastAPI(
    #     swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}}
    # )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Register routers
    app.include_router(model_info_controller.router, prefix="/api/info", tags=["Overview"])
    app.include_router(predict_controller.router, prefix="/api/predict", tags=["Prediction"])

    origins = [
        "http://localhost:4200",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # or ["*"] to allow all (not recommended for production)
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
        allow_headers=["*"],  # e.g., Authorization, Content-Type
    )

    # Custom Swagger UI with dark theme
    # @app.get("/docs", include_in_schema=False)
    # async def custom_swagger_ui_html():
    #     return get_swagger_ui_html(
    #         openapi_url="/openapi.json",
    #         title="Penguin Species Prediction API - Docs",
    #         swagger_js_url="/static/swagger-ui-bundle.js",
    #         swagger_css_url="/static/swagger-ui.css",
    #         # swagger_css_url="/static/swagger_ui_dark.min.css",
    #         swagger_favicon_url="/static/favicon.ico",
    #         swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # hide schema by default
    #     )

    # @app.get("/docs", include_in_schema=False)
    # async def custom_swagger_ui_html():
    #     return get_swagger_ui_html(
    #         openapi_url="/openapi.json",
    #         title="Penguin Species Prediction API - Docs",
    #         swagger_js_url="/static/swagger-ui-bundle.js",
    #         # swagger_css_url="/static/swagger_ui_dark.min.css",
    #         swagger_css_url="/static/swagger-ui.css",
    #         swagger_ui_parameters={
    #             "syntaxHighlight": {
    #                 "theme": "monokai"
    #             },
    #             "defaultModelsExpandDepth": -1
    #         }
    #     )

    # Trigger startup logic (like training model)
    @app.on_event("startup")
    async def on_startup():
        startup_service = StartupService()
        await startup_service.run()

    @app.on_event("startup")
    async def load_model_on_startup():
        await model_loader.load_model()

    return app
