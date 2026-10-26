import asyncio
import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot import types

DB_CONFIG = {
    "user": "bot_admin",
    "password": "my_secure_password",
    "database": "bot_database",
    "host": "192.168.1.100",
    "port": 5432
}
TEST_CURRENT_TG_ID = None
bot = AsyncTeleBot('8266635215:AAHYpAj1GheTN-ux7VFNvEH39Jn5eGtQfXY', parse_mode='HTML')
db_pool = None

@bot.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    async with db_pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS users(
                                id SERIAL PRIMARY KEY,
                                Name TEXT NOT NULL,
                                Tg_id BIGINT UNIQUE NOT NULL,
                                Admin BOOLEAN DEFAULT FALSE)""")

        await conn.execute("""CREATE TABLE IF NOT EXISTS shapka_tour(
                                id SERIAL PRIMARY KEY,
                                Name TEXT NOT NULL,
                                Login TEXT NOT NULL,
                                Password TEXT NOT NULL,
                                Created_admin TEXT NOT NULL,
                                Nam_users INTEGER DEFAULT 4,
                                Status TEXT)""")
    await bot.send_message(message.chat.id, "Бот запущен")

@bot.message_handler(commands=['new_user'])
async def kostil_user(message: types.Message):
    info = message.text.split()
    if len(info) < 3:
        await bot.send_message(message.chat.id, "Ошибка! Пиши так: /new_user <tg_id> <имя>")
        return
    print(info)
    tg_id = int(info[1])
    full_name = info[2]

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE Tg_id = $1;", tg_id)
        if not user:
            await conn.execute("""
                INSERT INTO users (Tg_id, Name) 
                VALUES ($1, $2) ON CONFLICT DO NOTHING
            """, tg_id, full_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить Турнир")
    btn2 = types.KeyboardButton("Мои турниры")
    markup.row(btn1, btn2)
    await bot.send_message(message.chat.id, f"Пользователь {full_name} успешно добавлен в базу!",reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Добавить Турнир")
async def log_tour_1(message: types.Message):
    sent_msg = bot.send_message(message.chat.id, "Ввидите логин и пароль турнира через пробле турнира \n \n Пример: \n tour123 12345")
    bot.register_next_step_handler(sent_msg, step_name)
async def log_tour_2(message):
    async with db_pool.acquire() as conn:
        log,pasw= message.text.split()
        tour = await conn.fetchrow("SELECT * FROM shapka_tour WHERE Login = $1;", log)
        if not tour:
            bot.send_message(message.chat.id, "Турнир не найден")
        
@bot.message_handler(commands=['maska'])
async def cmd_start(message: types.Message):
    global TEST_CURRENT_TG_ID
    us=message.text.split()
    TEST_CURRENT_TG_ID=us[1]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Добавить Турнир")
    btn2 = types.KeyboardButton("Мои турниры")
    markup.row(btn1, btn2)
    await bot.send_message(message.chat.id, f"Успешная смена на пользователя {TEST_CURRENT_TG_ID}",reply_markup=markup)
async def main():
    global db_pool
    print("Создаем пул соединений с базой данных...")
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    
    print("Бот вышел в онлайн!")
    await bot.polling(non_stop=True)

if __name__ == '__main__':
    asyncio.run(main())