from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/torneos/{id_torneo}/inscripciones")
def listar_inscripciones(id_torneo: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id_inscripcion, i.fecha_inscripcion, i.estado,
               p.tipo, i.id_participante,
               CASE p.tipo
                 WHEN 'J' THEN j.gamertag
                 WHEN 'E' THEN e.nombre
               END as nombre
        FROM inscripcion i
        JOIN participante p ON i.id_participante = p.id_participante
        LEFT JOIN jugador j ON p.id_participante = j.id_participante
        LEFT JOIN equipo e ON p.id_participante = e.id_participante
        WHERE i.id_torneo = %s
        ORDER BY i.fecha_inscripcion DESC
    """, (id_torneo,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "fecha": str(r[1]),
            "estado": r[2],
            "tipo": r[3],
            "id_participante": r[4],
            "nombre": r[5]
        }
        for r in rows
    ]

@router.post("/torneos/{id_torneo}/inscribir")
def inscribir(id_torneo: int, datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificar que el torneo está en inscripción
        cursor.execute(
            "SELECT estado, id_videojuego FROM torneo WHERE id_torneo = %s",
            (id_torneo,)
        )
        torneo = cursor.fetchone()
        if not torneo:
            return {"error": "Torneo no encontrado"}
        if torneo[0] != "Inscripcion":
            return {"error": "El torneo no está en fase de inscripción"}

        tipo = datos.get("tipo", "J")
        id_videojuego = torneo[1]

        if tipo == "J":
            # Inscripción individual
            id_jugador = datos["id_jugador"]

            # Verificar si ya tiene participante
            cursor.execute(
                "SELECT id_participante FROM jugador WHERE id_jugador = %s",
                (id_jugador,)
            )
            jugador = cursor.fetchone()

            if jugador and jugador[0]:
                id_participante = jugador[0]
            else:
                # Crear participante
                cursor.execute(
                    "INSERT INTO participante (tipo, id_videojuego, estado) VALUES (%s, %s, 'S') RETURNING id_participante",
                    (tipo, id_videojuego)
                )
                id_participante = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE jugador SET id_participante = %s WHERE id_jugador = %s",
                    (id_participante, id_jugador)
                )

        else:
            # Inscripción por equipo
            id_equipo = datos["id_equipo"]
            cursor.execute(
                "SELECT id_participante, id_capitan FROM equipo WHERE id_equipo = %s",
                (id_equipo,)
            )
            equipo = cursor.fetchone()
            if not equipo:
                return {"error": "Equipo no encontrado"}

            # Verificar que el que inscribe es el capitán
            if equipo[1] != datos["id_jugador"]:
                return {"error": "Solo el capitán puede inscribir al equipo"}

            id_participante = equipo[0]

        # Verificar que no esté ya inscrito
        cursor.execute(
            "SELECT id_inscripcion FROM inscripcion WHERE id_torneo = %s AND id_participante = %s",
            (id_torneo, id_participante)
        )
        if cursor.fetchone():
            return {"error": "Ya estás inscrito en este torneo"}

        # Crear inscripción
        cursor.execute(
            "INSERT INTO inscripcion (id_torneo, id_participante) VALUES (%s, %s) RETURNING id_inscripcion",
            (id_torneo, id_participante)
        )
        id_inscripcion = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Inscripción exitosa", "id_inscripcion": id_inscripcion}

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}