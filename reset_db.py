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
    
    await conn.execute("""CREATE TABLE users(
                            id SERIAL PRIMARY KEY,
                            Name TEXT NOT NULL,
                            Tg_id BIGINT UNIQUE NOT NULL,
                            Admin BOOLEAN DEFAULT FALSE)""")

    await conn.execute("""CREATE TABLE shapka_tour(
                            id SERIAL PRIMARY KEY,
                            Login TEXT NOT NULL,
                            Password TEXT NOT NULL,
                            Created_admin TEXT NOT NULL,
                            Nam_users INTEGER DEFAULT 4,
                            Status TEXT)""")

    await conn.execute("""CREATE TABLE jurnal(
                            id SERIAL PRIMARY KEY,
                            id_tour INTEGER REFERENCES shapka_tour(id),
                            id_user INTEGER REFERENCES users(id))""")

    await conn.execute("""CREATE TABLE matches(
                            id SERIAL PRIMARY KEY,
                            id_tour INTEGER REFERENCES shapka_tour(id),
                            user_1 INTEGER REFERENCES users(id),
                            user_2 INTEGER REFERENCES users(id),
                            win INTEGER REFERENCES users(id),
                            raund INTEGER NOT NULL)""")
                            
    await conn.close()
    print("База данных успешно обнулена и пересоздана!")

if __name__ == '__main__':
    asyncio.run(reset_database())