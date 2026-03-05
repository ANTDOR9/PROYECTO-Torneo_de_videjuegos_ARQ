-- ═══════════════════════════════════════════════════════════════
-- AQP GAMING — Script de Migración PostgreSQL
-- Todas las 18 entidades convertidas desde Oracle a PostgreSQL
-- Orden correcto para respetar dependencias entre tablas
-- ═══════════════════════════════════════════════════════════════

-- Limpiar si ya existe (útil para re-ejecutar)
DROP TABLE IF EXISTS valoracion         CASCADE;
DROP TABLE IF EXISTS incidencia         CASCADE;
DROP TABLE IF EXISTS premio             CASCADE;
DROP TABLE IF EXISTS partida_participante CASCADE;
DROP TABLE IF EXISTS partida            CASCADE;
DROP TABLE IF EXISTS fase               CASCADE;
DROP TABLE IF EXISTS torneo_patrocinador CASCADE;
DROP TABLE IF EXISTS equipo_patrocinador CASCADE;
DROP TABLE IF EXISTS patrocinador       CASCADE;
DROP TABLE IF EXISTS jugador_equipo     CASCADE;
DROP TABLE IF EXISTS jugador            CASCADE;
DROP TABLE IF EXISTS equipo             CASCADE;
DROP TABLE IF EXISTS participante       CASCADE;
DROP TABLE IF EXISTS arbitro            CASCADE;
DROP TABLE IF EXISTS torneo             CASCADE;
DROP TABLE IF EXISTS regla_videojuego   CASCADE;
DROP TABLE IF EXISTS videojuego         CASCADE;
DROP TABLE IF EXISTS genero             CASCADE;

-- ═══════════════════════════════════════════════════════════════
-- 1. GENERO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE genero (
    id_genero   SERIAL          PRIMARY KEY,
    nombre      VARCHAR(30)     NOT NULL UNIQUE,
    descripcion VARCHAR(200),
    icono_url   VARCHAR(150),
    activo      CHAR(1)         NOT NULL DEFAULT 'S',
    CONSTRAINT ck_genero_act CHECK (activo IN ('S','N'))
);

-- ═══════════════════════════════════════════════════════════════
-- 2. VIDEOJUEGO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE videojuego (
    id_videojuego   SERIAL      PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL UNIQUE,
    id_genero       INT         NOT NULL,
    desarrollador   VARCHAR(60),
    logo_url        VARCHAR(150),
    activo          CHAR(1)     NOT NULL DEFAULT 'S',
    CONSTRAINT fk_vjuego_gen FOREIGN KEY (id_genero) REFERENCES genero(id_genero),
    CONSTRAINT ck_vjuego_act CHECK (activo IN ('S','N'))
);

-- ═══════════════════════════════════════════════════════════════
-- 3. REGLA_VIDEOJUEGO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE regla_videojuego (
    id_regla        SERIAL      PRIMARY KEY,
    id_videojuego   INT         NOT NULL,
    nombre_regla    VARCHAR(60) NOT NULL,
    valor           VARCHAR(100) NOT NULL,
    tipo_valor      CHAR(1)     NOT NULL,
    descripcion     VARCHAR(300),
    activo          CHAR(1)     NOT NULL DEFAULT 'S',
    CONSTRAINT fk_regla_vjuego FOREIGN KEY (id_videojuego) REFERENCES videojuego(id_videojuego),
    CONSTRAINT ck_regla_tipo   CHECK (tipo_valor IN ('N','T','B')),
    CONSTRAINT ck_regla_act    CHECK (activo IN ('S','N'))
);

-- ═══════════════════════════════════════════════════════════════
-- 4. PARTICIPANTE (antes que JUGADOR y EQUIPO)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE participante (
    id_participante SERIAL      PRIMARY KEY,
    tipo            CHAR(1)     NOT NULL,
    id_videojuego   INT         NOT NULL,
    estado          CHAR(1)     NOT NULL DEFAULT 'S',
    CONSTRAINT fk_part_vjuego  FOREIGN KEY (id_videojuego) REFERENCES videojuego(id_videojuego),
    CONSTRAINT ck_part_tipo    CHECK (tipo IN ('J','E')),
    CONSTRAINT ck_part_estado  CHECK (estado IN ('S','N'))
);

-- ═══════════════════════════════════════════════════════════════
-- 5. JUGADOR
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE jugador (
    id_jugador      SERIAL       PRIMARY KEY,
    gamertag        VARCHAR(30)  NOT NULL UNIQUE,
    email           VARCHAR(120) NOT NULL UNIQUE,
    nombre          VARCHAR(60)  NOT NULL,
    fecha_registro  DATE         NOT NULL DEFAULT CURRENT_DATE,
    rango           VARCHAR(20),
    avatar          VARCHAR(255),
    id_participante INT          NOT NULL UNIQUE,
    CONSTRAINT fk_jug_part     FOREIGN KEY (id_participante) REFERENCES participante(id_participante),
    CONSTRAINT ck_jugador_rango CHECK (rango IN ('Bronce','Plata','Oro','Platino','Diamante') OR rango IS NULL)
);

-- ═══════════════════════════════════════════════════════════════
-- 6. EQUIPO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE equipo (
    id_equipo       SERIAL       PRIMARY KEY,
    nombre          VARCHAR(60)  NOT NULL,
    id_videojuego   INT          NOT NULL,
    id_capitan      INT          NOT NULL,
    logo_url        VARCHAR(150),
    activo          CHAR(1)      NOT NULL DEFAULT 'S',
    fecha_creacion  DATE,
    id_participante INT          NOT NULL UNIQUE,
    CONSTRAINT fk_equipo_vjuego FOREIGN KEY (id_videojuego)   REFERENCES videojuego(id_videojuego),
    CONSTRAINT fk_equipo_cap    FOREIGN KEY (id_capitan)       REFERENCES jugador(id_jugador),
    CONSTRAINT fk_equipo_part   FOREIGN KEY (id_participante)  REFERENCES participante(id_participante),
    CONSTRAINT ck_equipo_act    CHECK (activo IN ('S','N'))
);

-- ═══════════════════════════════════════════════════════════════
-- 7. JUGADOR_EQUIPO (puente N:M)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE jugador_equipo (
    id_jugador      INT     NOT NULL,
    id_equipo       INT     NOT NULL,
    fecha_ingreso   DATE    NOT NULL DEFAULT CURRENT_DATE,
    activo          CHAR(1) NOT NULL DEFAULT 'S',
    rol             VARCHAR(20),
    CONSTRAINT pk_je         PRIMARY KEY (id_jugador, id_equipo),
    CONSTRAINT fk_je_jugador FOREIGN KEY (id_jugador) REFERENCES jugador(id_jugador),
    CONSTRAINT fk_je_equipo  FOREIGN KEY (id_equipo)  REFERENCES equipo(id_equipo),
    CONSTRAINT ck_je_act     CHECK (activo IN ('S','N')),
    CONSTRAINT ck_je_rol     CHECK (rol IN ('Titular','Suplente','Coach','Analista') OR rol IS NULL)
);

-- ═══════════════════════════════════════════════════════════════
-- 8. ARBITRO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE arbitro (
    id_arbitro      SERIAL       PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    certificacion   VARCHAR(60),
    activo          CHAR(1)      NOT NULL DEFAULT 'S',
    CONSTRAINT ck_arb_act CHECK (activo IN ('S','N'))
);

-- ═══════════════════════════════════════════════════════════════
-- 9. TORNEO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE torneo (
    id_torneo       SERIAL       PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    id_videojuego   INT          NOT NULL,
    fecha_inicio    DATE         NOT NULL,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'Inscripcion',
    premio_total    NUMERIC(10,2),
    descripcion     TEXT,
    CONSTRAINT fk_torneo_vjuego FOREIGN KEY (id_videojuego) REFERENCES videojuego(id_videojuego),
    CONSTRAINT ck_torneo_est    CHECK (estado IN ('Inscripcion','En curso','Finalizado','Cancelado')),
    CONSTRAINT ck_torneo_prize  CHECK (premio_total >= 0 OR premio_total IS NULL)
);

-- ═══════════════════════════════════════════════════════════════
-- 10. FASE
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE fase (
    id_fase         SERIAL      PRIMARY KEY,
    id_torneo       INT         NOT NULL,
    nombre          VARCHAR(48) NOT NULL,
    orden           SMALLINT    NOT NULL,
    estado          VARCHAR(2)  NOT NULL DEFAULT 'PE',
    tipo_formato    VARCHAR(20) NOT NULL,
    tipo_bracket    VARCHAR(10),
    CONSTRAINT fk_fase_torneo FOREIGN KEY (id_torneo) REFERENCES torneo(id_torneo) ON DELETE CASCADE,
    CONSTRAINT ck_fase_est    CHECK (estado IN ('AC','FI','PE')),
    CONSTRAINT ck_fase_fmt    CHECK (tipo_formato IN ('ELIMINACION_SIMPLE','ELIMINACION_DOBLE','GRUPOS','BATTLE_ROYALE','ROUND_ROBIN')),
    CONSTRAINT ck_fase_brk    CHECK (tipo_bracket IN ('UPPER','LOWER','UNICO') OR tipo_bracket IS NULL),
    CONSTRAINT uq_fase_orden  UNIQUE (id_torneo, orden)
);

-- ═══════════════════════════════════════════════════════════════
-- 11. PARTIDA
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE partida (
    id_partida      SERIAL      PRIMARY KEY,
    id_fase         INT         NOT NULL,
    id_arbitro      INT         NOT NULL,
    fecha_hora      TIMESTAMP   NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'Programada',
    observaciones   TEXT,
    CONSTRAINT fk_partida_fase FOREIGN KEY (id_fase)    REFERENCES fase(id_fase)     ON DELETE CASCADE,
    CONSTRAINT fk_partida_arb  FOREIGN KEY (id_arbitro) REFERENCES arbitro(id_arbitro),
    CONSTRAINT ck_partida_est  CHECK (estado IN ('Programada','En juego','Finalizada','Cancelada'))
);

-- ═══════════════════════════════════════════════════════════════
-- 12. PARTIDA_PARTICIPANTE (puente N:M — reemplaza RESULTADO)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE partida_participante (
    id_partida      INT          NOT NULL,
    id_participante INT          NOT NULL,
    puesto_obtenido SMALLINT     NOT NULL,
    puntaje         NUMERIC(10,2) DEFAULT 0,
    mvp_jugador     INT,
    CONSTRAINT pk_pp          PRIMARY KEY (id_partida, id_participante),
    CONSTRAINT fk_pp_partida  FOREIGN KEY (id_partida)      REFERENCES partida(id_partida)           ON DELETE CASCADE,
    CONSTRAINT fk_pp_part     FOREIGN KEY (id_participante) REFERENCES participante(id_participante),
    CONSTRAINT fk_pp_mvp      FOREIGN KEY (mvp_jugador)     REFERENCES jugador(id_jugador),
    CONSTRAINT ck_pp_puesto   CHECK (puesto_obtenido > 0)
);

-- ═══════════════════════════════════════════════════════════════
-- 13. PATROCINADOR
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE patrocinador (
    id_patrocinador SERIAL       PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    ruc             CHAR(11)     NOT NULL UNIQUE,
    logo_url        VARCHAR(150),
    contacto        VARCHAR(60),
    email           VARCHAR(120),
    CONSTRAINT ck_pat_ruc CHECK (LENGTH(ruc) = 11)
);

-- ═══════════════════════════════════════════════════════════════
-- 14. TORNEO_PATROCINADOR (puente N:M)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE torneo_patrocinador (
    id_patrocinador INT          NOT NULL,
    id_torneo       INT          NOT NULL,
    tipo_visibilidad VARCHAR(20),
    monto           NUMERIC(10,2),
    fecha_acuerdo   DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_tp       PRIMARY KEY (id_patrocinador, id_torneo),
    CONSTRAINT fk_tp_pat   FOREIGN KEY (id_patrocinador) REFERENCES patrocinador(id_patrocinador),
    CONSTRAINT fk_tp_torneo FOREIGN KEY (id_torneo)      REFERENCES torneo(id_torneo) ON DELETE CASCADE,
    CONSTRAINT ck_tp_monto CHECK (monto >= 0 OR monto IS NULL)
);

-- ═══════════════════════════════════════════════════════════════
-- 15. EQUIPO_PATROCINADOR (puente N:M)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE equipo_patrocinador (
    id_patrocinador INT          NOT NULL,
    id_equipo       INT          NOT NULL,
    tipo_visibilidad VARCHAR(20),
    monto           NUMERIC(10,2),
    fecha_acuerdo   DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_ep       PRIMARY KEY (id_patrocinador, id_equipo),
    CONSTRAINT fk_ep_pat   FOREIGN KEY (id_patrocinador) REFERENCES patrocinador(id_patrocinador),
    CONSTRAINT fk_ep_equipo FOREIGN KEY (id_equipo)      REFERENCES equipo(id_equipo),
    CONSTRAINT ck_ep_monto CHECK (monto >= 0 OR monto IS NULL)
);

-- ═══════════════════════════════════════════════════════════════
-- 16. PREMIO
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE premio (
    id_premio       SERIAL       PRIMARY KEY,
    id_torneo       INT          NOT NULL,
    posicion        SMALLINT     NOT NULL,
    tipo            VARCHAR(20)  NOT NULL,
    valor           NUMERIC(10,2) NOT NULL,
    descripcion     VARCHAR(50),
    id_participante INT,
    CONSTRAINT fk_premio_torneo FOREIGN KEY (id_torneo)       REFERENCES torneo(id_torneo) ON DELETE CASCADE,
    CONSTRAINT fk_premio_part   FOREIGN KEY (id_participante) REFERENCES participante(id_participante),
    CONSTRAINT ck_premio_pos    CHECK (posicion IN (1,2,3)),
    CONSTRAINT ck_premio_tipo   CHECK (tipo IN ('Dinero','Periferico','Merchandising','Trofeo','Otro')),
    CONSTRAINT ck_premio_val    CHECK (valor > 0)
);

-- ═══════════════════════════════════════════════════════════════
-- 17. INCIDENCIA
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE incidencia (
    id_incidencia   SERIAL      PRIMARY KEY,
    id_partida      INT         NOT NULL,
    id_jugador      INT         NOT NULL,
    tipo            VARCHAR(30) NOT NULL,
    descripcion     TEXT        NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    momento         TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_inci_part FOREIGN KEY (id_partida) REFERENCES partida(id_partida) ON DELETE CASCADE,
    CONSTRAINT fk_inci_jug  FOREIGN KEY (id_jugador) REFERENCES jugador(id_jugador),
    CONSTRAINT ck_inci_est  CHECK (estado IN ('Pendiente','En revision','Resuelto'))
);

-- ═══════════════════════════════════════════════════════════════
-- 18. VALORACION
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE valoracion (
    id_valoracion   SERIAL  PRIMARY KEY,
    id_torneo       INT     NOT NULL,
    id_jugador      INT     NOT NULL,
    puntuacion      SMALLINT NOT NULL,
    comentario      TEXT,
    fecha           DATE    NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT fk_val_torneo FOREIGN KEY (id_torneo)  REFERENCES torneo(id_torneo) ON DELETE CASCADE,
    CONSTRAINT fk_val_jug    FOREIGN KEY (id_jugador) REFERENCES jugador(id_jugador),
    CONSTRAINT ck_val_punt   CHECK (puntuacion BETWEEN 1 AND 5),
    CONSTRAINT uq_val_torjug UNIQUE (id_torneo, id_jugador)
);

-- ═══════════════════════════════════════════════════════════════
-- ÍNDICES de rendimiento
-- ═══════════════════════════════════════════════════════════════
CREATE INDEX idx_jugador_email      ON jugador(email);
CREATE INDEX idx_jugador_gamertag   ON jugador(gamertag);
CREATE INDEX idx_partida_fase       ON partida(id_fase);
CREATE INDEX idx_partida_arbitro    ON partida(id_arbitro);
CREATE INDEX idx_pp_participante    ON partida_participante(id_participante);
CREATE INDEX idx_fase_torneo        ON fase(id_torneo);
CREATE INDEX idx_torneo_videojuego  ON torneo(id_videojuego);
CREATE INDEX idx_incidencia_partida ON incidencia(id_partida);
CREATE INDEX idx_valoracion_torneo  ON valoracion(id_torneo);

-- ═══════════════════════════════════════════════════════════════
-- FIN DEL SCRIPT — AQP GAMING
-- 18 tablas creadas correctamente
-- ═══════════════════════════════════════════════════════════════