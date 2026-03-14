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
    
@router.get("/jugadores/{id_jugador}/torneos")
def torneos_jugador(id_jugador: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id_torneo, t.nombre, t.estado, t.fecha_inicio,
               v.nombre as videojuego, i.fecha_inscripcion
        FROM inscripcion i
        JOIN torneo t ON i.id_torneo = t.id_torneo
        JOIN videojuego v ON t.id_videojuego = v.id_videojuego
        JOIN participante p ON i.id_participante = p.id_participante
        JOIN jugador j ON j.id_participante = p.id_participante
        WHERE j.id_jugador = %s
        ORDER BY i.fecha_inscripcion DESC
    """, (id_jugador,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "nombre": r[1],
            "estado": r[2],
            "fecha_inicio": str(r[3]),
            "videojuego": r[4],
            "fecha_inscripcion": str(r[5])
        }
        for r in rows
    ]

@router.put("/jugadores/{id_jugador}/rol")
def cambiar_rol(id_jugador: int, datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # No se puede cambiar el rol de un super_admin
        cursor.execute("SELECT rol FROM jugador WHERE id_jugador = %s", (id_jugador,))
        jugador = cursor.fetchone()
        if not jugador:
            return {"error": "Jugador no encontrado"}
        if jugador[0] == 'super_admin':
            return {"error": "No se puede modificar el rol de un super admin"}

        nuevo_rol = datos.get("rol")
        if nuevo_rol not in ['jugador', 'admin']:
            return {"error": "Rol inválido"}

        cursor.execute(
            "UPDATE jugador SET rol = %s WHERE id_jugador = %s",
            (nuevo_rol, id_jugador)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": f"Rol actualizado a {nuevo_rol}"}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}