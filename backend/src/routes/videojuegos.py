from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/videojuegos")
def listar_videojuegos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id_videojuego, v.nombre, g.nombre as genero, 
               v.desarrollador, v.activo
        FROM videojuego v
        JOIN genero g ON v.id_genero = g.id_genero
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "nombre": r[1],
            "genero": r[2],
            "desarrollador": r[3],
            "activo": r[4]
        }
        for r in rows
    ]

@router.post("/videojuegos")
def crear_videojuego(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO videojuego (nombre, id_genero, desarrollador, activo) 
           VALUES (%s, %s, %s, %s) RETURNING id_videojuego""",
        (datos["nombre"], datos["id_genero"], 
         datos.get("desarrollador"), datos.get("activo", "S"))
    )
    nuevo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"mensaje": "Videojuego creado", "id_videojuego": nuevo_id}