import asyncio
import asyncpg
import psycopg2
from async_orm.db_settings import (user_db_constant,
                                   password_db_constant,
                                   host_db_constant,
                                   database_db_constant,
                                   port_db_constant)

current_loop = asyncio.get_event_loop()


async def create_conn_cur():
    return await asyncpg.create_pool(user=user_db_constant,
                                     password=password_db_constant,
                                     host=host_db_constant,
                                     database=database_db_constant)


conn_pool = current_loop.run_until_complete(create_conn_cur())
psycopg_conn = psycopg2.connect(user=user_db_constant,
                                password=password_db_constant,
                                host=host_db_constant,
                                port=port_db_constant,
                                database=database_db_constant)
