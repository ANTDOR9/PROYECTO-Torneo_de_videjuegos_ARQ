from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File
import shutil, os
from src.database import get_connection
from src.routes.generos import router as generos_router
from src.routes.videojuegos import router as videojuegos_router
from src.routes.jugadores import router as jugadores_router
from src.routes.torneos import router as torneos_router
from src.routes.equipos import router as equipos_router
from src.routes.fases import router as fases_router
from src.routes.inscripciones import router as inscripciones_router
from src.routes.auth import router as auth_router

app = FastAPI(title="AQP Gaming", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
os.makedirs("avatares", exist_ok=True)
app.mount("/avatares", StaticFiles(directory="avatares"), name="avatares")

app.include_router(generos_router, prefix="/api")
app.include_router(videojuegos_router, prefix="/api")
app.include_router(jugadores_router, prefix="/api")
app.include_router(torneos_router, prefix="/api")
app.include_router(equipos_router, prefix="/api")
app.include_router(fases_router, prefix="/api")
app.include_router(inscripciones_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a AQP Gaming API"}

@app.get("/health")
def health():
    return {"estado": "funcionando"}

@app.post("/api/jugadores/{id_jugador}/avatar")
async def subir_avatar(id_jugador: int, archivo: UploadFile = File(...)):
    ext = archivo.filename.split(".")[-1]
    nombre_archivo = f"avatar_{id_jugador}.{ext}"
    ruta = f"avatares/{nombre_archivo}"
    with open(ruta, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/avatares/{nombre_archivo}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugador SET avatar = %s WHERE id_jugador = %s", (url, id_jugador))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Avatar actualizado", "url": url}

@app.get("/db-test")
def test_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM genero")
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"estado": "conexion exitosa", "registros_genero": resultado[0]}
    except Exception as e:
        return {"estado": "error", "detalle": str(e)}