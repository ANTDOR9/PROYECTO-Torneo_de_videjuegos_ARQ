from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/jugadores")
def listar_jugadores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_jugador, gamertag, email, nombre, 
               fecha_registro, rango, avatar
        FROM jugador
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "gamertag": r[1],
            "email": r[2],
            "nombre": r[3],
            "fecha_registro": str(r[4]),
            "rango": r[5],
            "avatar": r[6]
        }
        for r in rows
    ]

@router.post("/jugadores")
def crear_jugador(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Primero crear el PARTICIPANTE
        cursor.execute(
            """INSERT INTO participante (tipo, id_videojuego, estado) 
               VALUES (%s, %s, %s) RETURNING id_participante""",
            ('J', datos["id_videojuego"], 'S')
        )
        id_participante = cursor.fetchone()[0]

        # Luego crear el JUGADOR
        cursor.execute(
            """INSERT INTO jugador (gamertag, email, nombre, rango, id_participante)
               VALUES (%s, %s, %s, %s, %s) RETURNING id_jugador""",
            (datos["gamertag"], datos["email"], datos["nombre"],
             datos.get("rango"), id_participante)
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Jugador creado", "id_jugador": nuevo_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}