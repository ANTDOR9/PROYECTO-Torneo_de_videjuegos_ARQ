from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/torneos/{id_torneo}/fases")
def listar_fases(id_torneo: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_fase, nombre, orden, estado, tipo_formato, tipo_bracket
        FROM fase
        WHERE id_torneo = %s
        ORDER BY orden
    """, (id_torneo,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "nombre": r[1],
            "orden": r[2],
            "estado": r[3],
            "tipo_formato": r[4],
            "tipo_bracket": r[5]
        }
        for r in rows
    ]

@router.post("/torneos/{id_torneo}/fases")
def crear_fase(id_torneo: int, datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO fase (id_torneo, nombre, orden, estado, tipo_formato, tipo_bracket)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_fase""",
            (id_torneo, datos["nombre"], datos["orden"],
             datos.get("estado", "PE"), datos["tipo_formato"],
             datos.get("tipo_bracket"))
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Fase creada", "id_fase": nuevo_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}