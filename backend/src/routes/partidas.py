from fastapi import APIRouter
from src.database import get_connection

router = APIRouter()

@router.get("/fases/{id_fase}/partidas")
def listar_partidas(id_fase: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_partida, p.fecha_hora, p.estado, p.observaciones,
               pp1.id_participante as id_part1,
               pp2.id_participante as id_part2,
               CASE 
                 WHEN j1.gamertag IS NOT NULL THEN j1.gamertag
                 WHEN e1.nombre IS NOT NULL THEN e1.nombre
                 ELSE 'TBD'
               END as nombre1,
               CASE 
                 WHEN j2.gamertag IS NOT NULL THEN j2.gamertag
                 WHEN e2.nombre IS NOT NULL THEN e2.nombre
                 ELSE 'TBD'
               END as nombre2,
               pp1.puntaje as puntaje1,
               pp2.puntaje as puntaje2,
               pp1.puesto_obtenido as puesto1,
               pp2.puesto_obtenido as puesto2
        FROM partida p
        LEFT JOIN partida_participante pp1 ON pp1.id_partida = p.id_partida
        LEFT JOIN partida_participante pp2 ON pp2.id_partida = p.id_partida 
            AND pp2.id_participante > pp1.id_participante
        LEFT JOIN jugador j1 ON j1.id_participante = pp1.id_participante
        LEFT JOIN equipo e1 ON e1.id_participante = pp1.id_participante
        LEFT JOIN jugador j2 ON j2.id_participante = pp2.id_participante
        LEFT JOIN equipo e2 ON e2.id_participante = pp2.id_participante
        WHERE p.id_fase = %s
        AND pp1.id_participante IS NOT NULL
        ORDER BY p.fecha_hora
    """, (id_fase,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": r[0],
            "fecha_hora": str(r[1]),
            "estado": r[2],
            "observaciones": r[3],
            "participante1": {
                "id": r[4],
                "nombre": r[6],
                "puntaje": float(r[8]) if r[8] else None,
                "ganador": r[10] == 1 if r[10] else False
            },
            "participante2": {
                "id": r[5],
                "nombre": r[7],
                "puntaje": float(r[9]) if r[9] else None,
                "ganador": r[11] == 1 if r[11] else False
            }
        }
        for r in rows
    ]

@router.post("/fases/{id_fase}/partidas")
def crear_partida(id_fase: int, datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO partida (id_fase, fecha_hora, estado)
               VALUES (%s, %s, 'Programada') RETURNING id_partida""",
            (id_fase, datos.get("fecha_hora", "2026-01-01 00:00:00"))
        )
        id_partida = cursor.fetchone()[0]

        for idx, id_participante in enumerate(datos.get("participantes", [])):
            cursor.execute(
                """INSERT INTO partida_participante (id_partida, id_participante, puesto_obtenido, puntaje)
                   VALUES (%s, %s, %s, 0)""",
                (id_partida, id_participante, idx + 1)
            )

        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Partida creada", "id_partida": id_partida}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}

@router.put("/partidas/{id_partida}/resultado")
def registrar_resultado(id_partida: int, datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for resultado in datos.get("resultados", []):
            cursor.execute(
                """UPDATE partida_participante 
                   SET puntaje = %s, puesto_obtenido = %s
                   WHERE id_partida = %s AND id_participante = %s""",
                (resultado["puntaje"], resultado["puesto"],
                 id_partida, resultado["id_participante"])
            )

        cursor.execute(
            "UPDATE partida SET estado = 'Finalizada' WHERE id_partida = %s",
            (id_partida,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Resultado registrado"}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}