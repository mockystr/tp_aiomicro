from .model import Model
from .fields import (StringField, IntField, DateField,
                    FloatField, BooleanField)


class User(Model):
    email = StringField(required=True)
    password = StringField(required=True)
    name = StringField()
    created_date = DateField()
    last_login_date = DateField()

    def __str__(self):
        return 'User {}'.format(self.email, self.name)

    def __repr__(self):
        return '<User {}>'.format(self.email, self.name)

    class Meta:
        table_name = 'user'
        order_by = ('email',)


user_sql = """
CREATE TABLE "user" (
"id" BIGSERIAL PRIMARY KEY,
"email" VARCHAR(100) NOT NULL,
"password" VARCHAR(100) NOT NULL,
"name" VARCHAR(100),
"created_date" TIMESTAMP DEFAULT NULL,
"last_login_date" TIMESTAMP DEFAULT NULL);
"""


class Token(Model):
    token = StringField()
    user_id = IntField()
    expire_date = DateField()

    class Meta:
        table_name = 'token'


token_sql = """
CREATE TABLE "token" (
"id" BIGSERIAL PRIMARY KEY,
"token" TEXT NOT NULL,
"user_id" INTEGER REFERENCES "user" ("id") ON DELETE CASCADE NOT NULL,
"expire_date" TIMESTAMP NOT NULL);
"""


class CrawlerStats(Model):
    domain = StringField(required=True)
    author_id = IntField(required=True)
    https = IntField(required=True)
    time = DateField()
    pages_count = IntField()
    avg_time_per_page = FloatField()
    max_time_per_page = FloatField()
    min_time_per_page = FloatField()

    class Meta:
        table_name = 'crawler_stats'


crawler_stats_sql = """
CREATE TABLE "crawler_stats" (
"id" BIGSERIAL PRIMARY KEY,
"domain" VARCHAR(255) NOT NULL,
"author_id" INTEGER REFERENCES "user" ("id"),
"https" INTEGER NOT NULL,
"time" TIMESTAMP,
"pages_count" INTEGER,
"avg_time_per_page" FLOAT,
"max_time_per_page" FLOAT,
"min_time_per_page" FLOAT);
"""
