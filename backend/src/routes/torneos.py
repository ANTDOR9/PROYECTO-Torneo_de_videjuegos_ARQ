from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/torneos")
def listar_torneos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id_torneo, t.nombre, v.nombre as videojuego,
               t.fecha_inicio, t.estado, t.premio_total
        FROM torneo t
        JOIN videojuego v ON t.id_videojuego = v.id_videojuego
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "nombre": r[1],
            "videojuego": r[2],
            "fecha_inicio": str(r[3]),
            "estado": r[4],
            "premio_total": float(r[5]) if r[5] else None
        }
        for r in rows
    ]

@router.post("/torneos")
def crear_torneo(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO torneo (nombre, id_videojuego, fecha_inicio, estado, premio_total, descripcion)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_torneo""",
            (datos["nombre"], datos["id_videojuego"], datos["fecha_inicio"],
             datos.get("estado", "Inscripcion"), datos.get("premio_total"),
             datos.get("descripcion"))
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Torneo creado", "id_torneo": nuevo_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}

@router.get("/torneos/{id_torneo}")
def detalle_torneo(id_torneo: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id_torneo, t.nombre, v.nombre as videojuego,
               t.fecha_inicio, t.estado, t.premio_total, t.descripcion
        FROM torneo t
        JOIN videojuego v ON t.id_videojuego = v.id_videojuego
        WHERE t.id_torneo = %s
    """, (id_torneo,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return {"error": "Torneo no encontrado"}
    return {
        "id": row[0],
        "nombre": row[1],
        "videojuego": row[2],
        "fecha_inicio": str(row[3]),
        "estado": row[4],
        "premio_total": float(row[5]) if row[5] else None,
        "descripcion": row[6]
    }