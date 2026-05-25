from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main_route():
    return {"Hello": "World"}

@app.get("/ready")
def ready():
    return {"status": 200}
