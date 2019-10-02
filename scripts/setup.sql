\connect tp_aiomicro

-- DROP TABLE IF EXISTS "crawler_stats";
-- DROP TABLE IF EXISTS "token";
-- DROP TABLE IF EXISTS "users";

CREATE TABLE IF NOT EXISTS "users" (
"id" BIGSERIAL PRIMARY KEY,
"email" VARCHAR(100) NOT NULL,
"password" VARCHAR(100) NOT NULL,
"name" VARCHAR(100),
"created_date" TIMESTAMP DEFAULT NULL,
"last_login_date" TIMESTAMP DEFAULT NULL);

CREATE TABLE IF NOT EXISTS "tokens" (
"id" BIGSERIAL PRIMARY KEY,
"token" TEXT NOT NULL,
"user_id" INTEGER REFERENCES "users" ("id") ON DELETE CASCADE,
"expire_date" TIMESTAMP NOT NULL);

CREATE TABLE IF NOT EXISTS "crawler_stats" (
"id" BIGSERIAL PRIMARY KEY,
"domain" VARCHAR(255) NOT NULL,
"author_id" INTEGER REFERENCES "users" ("id") ON DELETE SET NULL,
"https" INTEGER NOT NULL,
"time" TIMESTAMP,
"pages_count" INTEGER,
"avg_time_per_page" FLOAT,
"max_time_per_page" FLOAT,
"min_time_per_page" FLOAT);