import asyncio
import asyncpg

DB_CONFIG = {
    "user": "bot_admin",
    "password": "my_secure_password",
    "database": "bot_database",
    "host": "192.168.1.100",
    "port": 5432
}

async def reset_database():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    await conn.execute("DROP TABLE IF EXISTS matches CASCADE;")
    await conn.execute("DROP TABLE IF EXISTS jurnal CASCADE;")
    await conn.execute("DROP TABLE IF EXISTS shapka_tour CASCADE;")
    await conn.execute("DROP TABLE IF EXISTS users CASCADE;")
                            
    await conn.close()
    print("Таблицы успешно удалены!")

if __name__ == '__main__':
    asyncio.run(reset_database())