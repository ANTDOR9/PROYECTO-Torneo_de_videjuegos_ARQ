from fastapi import APIRouter
from src.database import get_connection
from src.auth import encriptar_password, verificar_password, crear_token

router = APIRouter()

@router.post("/registro")
def registro(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el email ya existe
        cursor.execute("SELECT id_jugador FROM jugador WHERE email = %s", (datos["email"],))
        if cursor.fetchone():
            return {"error": "El email ya está registrado"}

        # Encriptar contraseña
        password_hash = encriptar_password(datos["password"])

        # Crear participante
        cursor.execute(
            """INSERT INTO participante (tipo, id_videojuego, estado)
               VALUES (%s, %s, %s) RETURNING id_participante""",
            ('J', datos["id_videojuego"], 'S')
        )
        id_participante = cursor.fetchone()[0]

        # Crear jugador
        cursor.execute(
            """INSERT INTO jugador (gamertag, email, nombre, rango, id_participante, password_hash)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_jugador""",
            (datos["gamertag"], datos["email"], datos["nombre"],
             datos.get("rango"), id_participante, password_hash)
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"mensaje": "Cuenta creada exitosamente", "id_jugador": nuevo_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return {"error": str(e)}

@router.post("/login")
def login(datos: dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id_jugador, gamertag, nombre, password_hash FROM jugador WHERE email = %s",
            (datos["email"],)
        )
        jugador = cursor.fetchone()
        cursor.close()
        conn.close()

        if not jugador:
            return {"error": "Email o contraseña incorrectos"}

        if not verificar_password(datos["password"], jugador[3]):
            return {"error": "Email o contraseña incorrectos"}

        token = crear_token({
            "id": jugador[0],
            "gamertag": jugador[1],
            "nombre": jugador[2]
        })

        return {
            "mensaje": "Login exitoso",
            "token": token,
            "jugador": {
                "id": jugador[0],
                "gamertag": jugador[1],
                "nombre": jugador[2]
            }
        }
    except Exception as e:
        return {"error": str(e)}