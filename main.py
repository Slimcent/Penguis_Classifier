import uvicorn
from Core.app_builder import create_app

app = create_app()
print("main entrance")
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

