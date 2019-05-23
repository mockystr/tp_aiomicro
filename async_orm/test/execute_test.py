import asyncio
import asyncpg
from utils import current_loop
from model_async import psycopg_conn, conn_pool


async def testing_update():
    con = conn_pool.acquire()
    res = await con.execute('INSERT 1')
    await conn_pool.release(con)
    return res


if __name__ == '__main__':
    current_loop.run_until_complete(testing_update())
    # ...
