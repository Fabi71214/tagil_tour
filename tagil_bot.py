#ПОДГОТОВКА
import asyncio
import asyncpg
from telebot.async_telebot import AsyncTeleBot
from telebot import types
user_states={}
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

#СТАРТ
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

        await conn.execute("""CREATE TABLE IF NOT EXISTS jurnal(
                                id SERIAL PRIMARY KEY,
                                id_tour INTEGER REFERENCES shapka_tour(id),
                                id_user INTEGER REFERENCES users(id))""")

        await conn.execute("""CREATE TABLE IF NOT EXISTS matches(
                                id SERIAL PRIMARY KEY,
                                id_tour INTEGER REFERENCES shapka_tour(id),
                                user_1 INTEGER REFERENCES users(id),
                                user_2 INTEGER REFERENCES users(id),
                                win INTEGER REFERENCES users(id),
                                raund INTEGER NOT NULL)""")
    await bot.send_message(message.chat.id, "Бот запущен")

#ДОБОВЛЕНИЕ ЮСЕР(ДЕМО)
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

#РЕАЛИЗАЦЫЯ ФУНКЦЫОНАЛА ИГРОКА
#добавить турнир
@bot.message_handler(func=lambda message: message.text == "Добавить Турнир")
async def log_tour_1(message: types.Message):
    sent_msg = await bot.send_message(message.chat.id, "Ввидите логин и пароль турнира через пробле \n \n Пример: \n tour123 12345")
    user_states[message.chat.id] = "waiting_for_tour_data"
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_for_tour_data")
async def log_tour_2(message: types.Message):
    user_states[message.chat.id] = None
    async with db_pool.acquire() as conn:
        lp=message.text.split()
        if len(lp)==2:
            log,pasw= lp[0],lp[1]
            print(lp)
            tour = await conn.fetchrow("SELECT * FROM shapka_tour WHERE Login = $1;", log)
            if not tour:
                await bot.send_message(message.chat.id, "Турнир не найден")
        else:
            await bot.send_message(message.chat.id, "Сообщение введено неправильно")
#посмотреть турниры
@bot.message_handler(func=lambda message: message.text == "Мои турниры")
async def send_tour_1(message: types.Message):
        user_states[message.chat.id] = "send_for_tour_data"
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "send_for_tour_data")
async def log_tour_2(message: types.Message):
    user_states[message.chat.id] = None

#МАСКА ДЛЯ ТЕСТИРОВАНИЯ
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

#ПОДКЛЮЧЕНИЕ БОТА И БД
async def main():
    global db_pool
    print("Создаем пул соединений с базой данных...")
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    
    print("Бот вышел в онлайн!")
    await bot.polling(non_stop=True)
if __name__ == '__main__':
    asyncio.run(main())