# PROYECTO-Torneo_de_videjuegos_ARQ
Proyecto SQL para probar conexiones en tiempo real, almacenamiento de datos y programa totalmente funcional 
bien ya tengo tu imagen, de esto vamos a trabajar nop? :3 
~~~
aqp-gaming/
├── backend/
│   ├── src/
│   │   ├── routes/        ← endpoints de la API
│   │   ├── controllers/   ← lógica de negocio
│   │   ├── models/        ← entidades de la BD
│   │   └── middlewares/
│   ├── database/
│   │   ├── migrations/    ← scripts SQL de creación
│   │   └── seeds/         ← datos de prueba
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/      ← llamadas a la API
│   └── package.json
├── .gitignore
├── README.md
└── .env.example           ← variables de entorno SIN valores reales
~~~
falta construir estoo mayoooo:
~~~
Lo que el usuario ve          Lo que ya tienes
─────────────────────         ─────────────────
Página web con diseño    ←→   FastAPI (backend)
Formulario de registro   ←→   Endpoint /jugadores
Lista de torneos         ←→   Endpoint /torneos
Bracket visual           ←→   Endpoint /fases
...
~~~

actuazlizacion de archivos HTML:
~~~
frontend/
├── pages/
│   ├── index.html        ← página principal con lista de torneos
│   ├── torneo.html       ← detalle de un torneo con sus fases
│   ├── registro.html     ← registrar jugador nuevo
│   └── equipos.html      ← ver y crear equipos
├── components/
│   └── navbar.html       ← barra de navegación reutilizable
└── services/
    └── api.js            ← funciones para llamar al backend


sistema de competitividad

Cuartos          Semis          Final
Team A ─┐
         ├─ Team A ─┐
Team B ─┘            ├─ Team A 🏆
Team C ─┐            │
         ├─ Team C ─┘
Team D ─┘



Backend ✅

FastAPI con 7 endpoints funcionando
Sistema de login y registro con JWT
Subida de avatares
Conectado a PostgreSQL en Railway

Base de datos ✅

18 tablas diseñadas y creadas
Datos iniciales cargados
Corriendo en la nube 24/7

Frontend ✅

Página principal con video de fondo
Página de registro y login
Página de perfil con foto
Página de detalle de torneo con bracket
Estilo gamer rojo/negro
Desplegado en Vercel
~~~
LOGRAAAMOOOOOOOOOOOOOOOOSSSSSSSSSSSSSSSSSSS WIIIIIIIIIIIIIIIIIIIIIIIII
Lo que falta para tener una app completa: (actualizacion :3) 

Panel admin con crear torneos ✅
Sistema de roles super_admin/admin/jugador ✅
Bracket con datos reales — ahora muestra TBD
Página de detalle de equipo — miembros, imagen
Crear torneo desde admin ✅

~~~

Página de equipos — nunca se terminó, es una página rota en la navbar
Inscribirse a un torneo — sin esto la app no tiene sentido competitivo
Crear torneo desde la web — ahora solo se puede desde Swagger
Bracket con datos reales — ahora muestra TBD, necesita partidas reales
Panel de administrador — para gestionar torneos, jugadores y resultados
Perfil con historial — mostrar torneos en los que participó el jugador
