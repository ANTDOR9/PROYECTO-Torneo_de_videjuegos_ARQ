from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/equipos")
def listar_equipos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id_equipo, e.nombre, v.nombre as videojuego,
               j.gamertag as capitan, e.activo, e.fecha_creacion
        FROM equipo e
        JOIN videojuego v ON e.id_videojuego = v.id_videojuego
        JOIN jugador j ON e.id_capitan = j.id_jugador
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "nombre": r[1],
            "videojuego": r[2],
            "capitan": r[3],
            "activo": r[4],
            "fecha_creacion": str(r[5]) if r[5] else None
        }
        for r in rows
    ]

@router.post("/equipos")
def crear_equipo(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Primero crear el PARTICIPANTE tipo Equipo
        cursor.execute(
            """INSERT INTO participante (tipo, id_videojuego, estado)
               VALUES (%s, %s, %s) RETURNING id_participante""",
            ('E', datos["id_videojuego"], 'S')
        )
        id_participante = cursor.fetchone()[0]

        # Luego crear el EQUIPO
        cursor.execute(
            """INSERT INTO equipo (nombre, id_videojuego, id_capitan, activo, fecha_creacion, id_participante)
               VALUES (%s, %s, %s, %s, CURRENT_DATE, %s) RETURNING id_equipo""",
            (datos["nombre"], datos["id_videojuego"], datos["id_capitan"],
             datos.get("activo", "S"), id_participante)
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Equipo creado", "id_equipo": nuevo_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}