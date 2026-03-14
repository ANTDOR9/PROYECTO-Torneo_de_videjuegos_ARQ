from fastapi import APIRouter
from src.database import get_connection
import random
import string

router = APIRouter()

def generar_codigo():
    caracteres = string.ascii_uppercase + string.digits
    return 'AQP-' + ''.join(random.choices(caracteres, k=4))

@router.get("/equipos")
def listar_equipos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id_equipo, e.nombre, v.nombre as videojuego,
               j.gamertag as capitan, e.activo, e.fecha_creacion,
               e.codigo_invitacion
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
            "fecha_creacion": str(r[5]) if r[5] else None,
            "codigo_invitacion": r[6]
        }
        for r in rows
    ]

@router.post("/equipos")
def crear_equipo(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO participante (tipo, id_videojuego, estado)
               VALUES (%s, %s, %s) RETURNING id_participante""",
            ('E', datos["id_videojuego"], 'S')
        )
        id_participante = cursor.fetchone()[0]

        codigo = generar_codigo()
        # Asegurar que el código sea único
        while True:
            cursor.execute("SELECT id_equipo FROM equipo WHERE codigo_invitacion = %s", (codigo,))
            if not cursor.fetchone():
                break
            codigo = generar_codigo()

        cursor.execute(
            """INSERT INTO equipo (nombre, id_videojuego, id_capitan, activo, fecha_creacion, id_participante, codigo_invitacion)
               VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s) RETURNING id_equipo""",
            (datos["nombre"], datos["id_videojuego"], datos["id_capitan"],
             datos.get("activo", "S"), id_participante, codigo)
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Equipo creado", "id_equipo": nuevo_id, "codigo_invitacion": codigo}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}

@router.post("/equipos/unirse")
def unirse_equipo(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Buscar equipo por código
        cursor.execute(
            "SELECT id_equipo, id_videojuego FROM equipo WHERE codigo_invitacion = %s AND activo = 'S'",
            (datos["codigo"],)
        )
        equipo = cursor.fetchone()
        if not equipo:
            return {"error": "Código inválido o equipo no encontrado"}

        id_equipo = equipo[0]

        # Verificar que no esté ya en el equipo
        cursor.execute(
            "SELECT id_jugador FROM jugador_equipo WHERE id_jugador = %s AND id_equipo = %s AND activo = 'S'",
            (datos["id_jugador"], id_equipo)
        )
        if cursor.fetchone():
            return {"error": "Ya eres miembro de este equipo"}

        # Unirse al equipo
        cursor.execute(
            """INSERT INTO jugador_equipo (id_jugador, id_equipo, fecha_ingreso, activo, rol)
               VALUES (%s, %s, CURRENT_DATE, 'S', 'Titular')""",
            (datos["id_jugador"], id_equipo)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Te uniste al equipo exitosamente"}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}



@router.get("/equipos/{id_equipo}")
def detalle_equipo(id_equipo: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Info del equipo
        cursor.execute("""
            SELECT e.id_equipo, e.nombre, v.nombre as videojuego,
                   j.gamertag as capitan, e.activo, e.fecha_creacion,
                   e.codigo_invitacion, e.imagen
            FROM equipo e
            JOIN videojuego v ON e.id_videojuego = v.id_videojuego
            JOIN jugador j ON e.id_capitan = j.id_jugador
            WHERE e.id_equipo = %s
        """, (id_equipo,))
        equipo = cursor.fetchone()

        if not equipo:
            return {"error": "Equipo no encontrado"}

        # Miembros del equipo
        cursor.execute("""
            SELECT j.id_jugador, j.gamertag, j.avatar, j.rango,
                   je.rol, je.fecha_ingreso
            FROM jugador_equipo je
            JOIN jugador j ON je.id_jugador = j.id_jugador
            WHERE je.id_equipo = %s AND je.activo = 'S'
            ORDER BY je.fecha_ingreso ASC
        """, (id_equipo,))
        miembros = cursor.fetchall()

        cursor.close()
        conn.close()
        return {
            "id": equipo[0],
            "nombre": equipo[1],
            "videojuego": equipo[2],
            "capitan": equipo[3],
            "activo": equipo[4],
            "fecha_creacion": str(equipo[5]) if equipo[5] else None,
            "codigo_invitacion": equipo[6],
            "imagen": equipo[7] if len(equipo) > 7 else None,
            "miembros": [
                {
                    "id": m[0],
                    "gamertag": m[1],
                    "avatar": m[2],
                    "rango": m[3],
                    "rol": m[4],
                    "fecha_ingreso": str(m[5]) if m[5] else None
                }
                for m in miembros
            ]
        }
    except Exception as e:
        cursor.close()
        conn.close()
        return {"error": str(e)}