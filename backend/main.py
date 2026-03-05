from fastapi import FastAPI

app = FastAPI(title="AQP Gaming", version="1.0.0")

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a AQP Gaming API"}

@app.get("/health")
def health():
    return {"estado": "funcionando"}