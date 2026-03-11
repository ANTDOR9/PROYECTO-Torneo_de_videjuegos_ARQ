from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/generos")
def listar_generos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_genero, nombre, descripcion, activo FROM genero")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"id": r[0], "nombre": r[1], "descripcion": r[2], "activo": r[3]}
        for r in rows
    ]

@router.post("/generos")
def crear_genero(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO genero (nombre, descripcion, activo) VALUES (%s, %s, %s) RETURNING id_genero",
        (datos["nombre"], datos.get("descripcion"), datos.get("activo", "S"))
    )
    nuevo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Genero creado", "id_genero": nuevo_id}