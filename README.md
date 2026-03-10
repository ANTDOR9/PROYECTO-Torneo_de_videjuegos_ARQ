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
