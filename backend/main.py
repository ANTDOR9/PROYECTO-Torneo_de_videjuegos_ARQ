from fastapi import FastAPI
from src.database import get_connection
from src.routes.generos import router as generos_router
from src.routes.videojuegos import router as videojuegos_router
from src.routes.jugadores import router as jugadores_router
from src.routes.torneos import router as torneos_router
from src.routes.equipos import router as equipos_router
from src.routes.fases import router as fases_router

app = FastAPI(title="AQP Gaming", version="1.0.0")

app.include_router(generos_router, prefix="/api")
app.include_router(videojuegos_router, prefix="/api")
app.include_router(jugadores_router, prefix="/api")
app.include_router(torneos_router, prefix="/api")
app.include_router(equipos_router, prefix="/api")
app.include_router(fases_router, prefix="/api")

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a AQP Gaming API"}

@app.get("/health")
def health():
    return {"estado": "funcionando"}

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