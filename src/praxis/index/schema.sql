-- Схема индекса Praxis (реальный путь для v1).
-- Один Postgres хранит метаданные, полнотекст (FTS, русская конфигурация) и
-- плотные векторы (pgvector) — минимум движущихся частей для старта.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS acts (
    id          text PRIMARY KEY,
    kind        text NOT NULL,
    title       text NOT NULL,
    short_title text NOT NULL,
    number      text,
    date        text,
    edition     text
);

CREATE TABLE IF NOT EXISTS provisions (
    id             text PRIMARY KEY,
    act_id         text NOT NULL REFERENCES acts(id) ON DELETE CASCADE,
    article_number text NOT NULL,
    article_title  text NOT NULL,
    path           text NOT NULL DEFAULT '',
    text           text NOT NULL,
    position       int  NOT NULL,
    edition        text,
    embedding      vector(1024),  -- BGE-M3
    fts            tsvector GENERATED ALWAYS AS (to_tsvector('russian', text)) STORED
);

CREATE INDEX IF NOT EXISTS provisions_fts_idx
    ON provisions USING gin (fts);

CREATE INDEX IF NOT EXISTS provisions_embedding_idx
    ON provisions USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS provisions_act_idx
    ON provisions (act_id);
