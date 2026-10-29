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
vrem_tour={}
TEST_CURRENT_TG_ID = 8048744008
bot = AsyncTeleBot('8266635215:AAHYpAj1GheTN-ux7VFNvEH39Jn5eGtQfXY', parse_mode='HTML')
db_pool = None
#клавиатуры
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Добавить Турнир")
btn2 = types.KeyboardButton("Мои турниры")
markup.row(btn1, btn2)

admin_kea = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_admin1= types.KeyboardButton("Создать турнир")
btn_admin2= types.KeyboardButton("Вести турнир")
admin_kea.row(btn1,btn2)
admin_kea.row(btn_admin1)
admin_kea.row(btn_admin2)
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
        user = await conn.fetchrow("SELECT * FROM users WHERE Tg_id = $1;", message.chat.id)
        texst_mesg=""
        if not user:
            await conn.execute("""
                INSERT INTO users (Tg_id, Name) 
                VALUES ($1, $2) ON CONFLICT DO NOTHING
            """, message.chat.id, message.from_user.first_name)
            texst_mesg="Вы успешно зарегестрированны!"
        else:
            texst_mesg="Вы уже зарегистрированны :)"
        chek_admin=await conn.fetchrow("""SELECT Admin FROM users WHERE Tg_id = $1;""",message.chat.id)
    kea=None
    if chek_admin and chek_admin['admin']:
        kea=admin_kea
    else:
        kea=markup
    TEST_CURRENT_TG_ID=message.chat.id
    await bot.send_message(message.chat.id, f"{texst_mesg}\n \n Клавиатура обновленна",reply_markup=kea)
#ДОБОВЛЕНИЕ ЮСЕР(ДЕМО)
@bot.message_handler(commands=['new_user'])
async def kostil_user(message: types.Message):
    info = message.text.split()
    if len(info) < 3:
        await bot.send_message(message.chat.id, "Ошибка! Пиши так: /new_user <tg_id> <имя>")
        return

    tg_id = int(info[1])
    full_name = info[2]

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE Tg_id = $1;", tg_id)
        if not user:
            await conn.execute("""
                INSERT INTO users (Tg_id, Name) 
                VALUES ($1, $2) ON CONFLICT DO NOTHING
            """, tg_id, full_name)
    await bot.send_message(message.chat.id, f"Пользователь {full_name} успешно добавлен в базу!")

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
            us_id = await conn.fetchrow("SELECT * FROM users WHERE Tg_id = $1;", TEST_CURRENT_TG_ID)
            if not tour:
                await bot.send_message(message.chat.id, "Турнир не найден")
            else:
                if pasw==tour["password"]:
                    await conn.execute("""
                        INSERT INTO jurnal (id_tour, id_user) 
                        VALUES ($1, $2)
                    """,tour['id'],us_id['id'])
                    await bot.send_message(message.chat.id, f"Вы успешно добавлены на турнир {log}")
                else:
                    await bot.send_message(message.chat.id, "Неверный пароль")
        else:
            await bot.send_message(message.chat.id, "Сообщение введено неправильно")
#посмотреть турниры
@bot.message_handler(func=lambda message: message.text == "Мои турниры")
async def send_tour_1(message: types.Message):
    async with db_pool.acquire() as conn:
        tour=await conn.fetch('''
        SELECT shapka_tour.* 
        FROM shapka_tour
        JOIN jurnal ON shapka_tour.id = jurnal.id_tour
        JOIN users ON jurnal.id_user = users.id
        WHERE users.Tg_id = $1;''',TEST_CURRENT_TG_ID)

    if not tour:
        await bot.send_message(message.chat.id, "У вас нет турниров")
    else:
        print(tour)

#РЕАЛИЗАЦЫЯ ФУНКЦЫОНАЛА АДМИНА
#добовление админа
@bot.message_handler(func=lambda message: message.text == "otec_andrey")
async def add_admin(message: types.Message):
    async with db_pool.acquire() as conn:
        await conn.execute("""UPDATE users
                                SET Admin = TRUE
                                WHERE Tg_id = $1;""",TEST_CURRENT_TG_ID)
    await bot.send_message(message.chat.id, f"Вы повышаны до админа!",reply_markup=admin_kea)
@bot.message_handler(func=lambda message: message.text == "ne_otec_andrey")
async def clouse_admin(message: types.Message):
    async with db_pool.acquire() as conn:
        await conn.execute("""UPDATE users
                                SET Admin = FALSE
                                WHERE Tg_id = $1;""",TEST_CURRENT_TG_ID)
    await bot.send_message(message.chat.id, f"Вы понижены до юсера :(",reply_markup=markup)

#создание турнира
@bot.message_handler(func=lambda message: message.text == "Создать турнир")
async def add_tour_1(message: types.Message):
    async with db_pool.acquire() as conn:
        chek_admin=await conn.fetchrow("""SELECT Admin FROM users
                                WHERE Tg_id = $1;""",TEST_CURRENT_TG_ID)
        if chek_admin and chek_admin['admin']:
            kol_vo_user = types.InlineKeyboardMarkup() 
            btn4 = types.InlineKeyboardButton(text="4", callback_data="size_4")
            btn8 = types.InlineKeyboardButton(text="8", callback_data="size_8")
            btn16 = types.InlineKeyboardButton(text="16", callback_data="size_16")
            kol_vo_user.row(btn4,btn8,btn16)
            await bot.send_message(message.chat.id,"Выберете кол-во учасников",reply_markup=kol_vo_user)
@bot.callback_query_handler(func=lambda call: call.data.startswith('size_'))
async def add_tour_2(call: types.CallbackQuery):
    global vrem_tour
    if call.message.chat.id not in vrem_tour:
        vrem_tour[call.message.chat.id] = {}
    vrem_tour[call.message.chat.id]["kol_vo"]=call.data.split('_')[1]
    await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Отлично! Турнир на {vrem_tour[call.message.chat.id]['kol_vo']} человек.\nТеперь введите Логин и Пароль через пробел:")
    vrem_tour[call.message.chat.id]['msg_id'] = call.message.message_id
    user_states[call.message.chat.id] = "login_password_tour"
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "login_password_tour")
async def add_tour_3(message: types.Message):
    user_states[message.chat.id] = None
    bot.delete_message(chat_id=message.chat.id, message_id=vrem_tour[message.chat.id]['msg_id'])
    if len(message.text.split())==2:
        log,pasw=message.text.split()
        if message.chat.id not in vrem_tour:
            vrem_tour[message.chat.id] = {}
        vrem_tour[message.chat.id]['pasw']=pasw
        vrem_tour[message.chat.id]['log']=log
        async with db_pool.acquire() as conn:
            tour = await conn.fetchrow("SELECT * FROM shapka_tour WHERE Login = $1;", log)
        if tour:
            await bot.send_message(chat_id=message.chat.id,text="Такой тур уже есть")
        else:
            yes_or_no = types.InlineKeyboardMarkup() 
            btn_yes = types.InlineKeyboardButton(text="Да", callback_data="answer_yes")
            btn_no = types.InlineKeyboardButton(text="Нет", callback_data="answer_no")
            yes_or_no.row(btn_yes,btn_no)
            await bot.send_message(
                        chat_id=message.chat.id,
                        text=f"Проверьте данные:\nЛогин: {log}\nПароль: {pasw}\n\nВсё верно?",
                        reply_markup=yes_or_no
                    )
    else:
        if message.chat.id in vrem_tour:
            del vrem_tour[message.chat.id] 
        await bot.send_message(message.chat.id,"Неверно построино сообщение")
@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
async def add_tour_4(call: types.CallbackQuery):
    answer=call.data.split('_')[1]

    if answer=="yes":
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO shapka_tour (Login,Password,Created_admin,Nam_users,Status) 
                VALUES ($1, $2, $3, $4, $5)
            """,vrem_tour[call.message.chat.id]["log"], vrem_tour[call.message.chat.id]["pasw"],str(TEST_CURRENT_TG_ID), int(vrem_tour[call.message.chat.id]["kol_vo"]),"set")
        
        await bot.send_message(call.message.chat.id, "Турнир успешно создан")
    else:
        await bot.send_message(call.message.chat.id, "Создание турнира отменено")
    if call.message.chat.id in vrem_tour:
        del vrem_tour[call.message.chat.id]  
    await bot.answer_callback_query(call.id)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)    

#МАСКА ДЛЯ ТЕСТИРОВАНИЯ
@bot.message_handler(commands=['maska'])
async def cmd_start(message: types.Message):
    global TEST_CURRENT_TG_ID
    us=message.text.split()
    TEST_CURRENT_TG_ID=int(us[1])
    async with db_pool.acquire() as conn:
        chek_admin=await conn.fetchrow("""SELECT Admin FROM users WHERE Tg_id = $1;""",TEST_CURRENT_TG_ID)
    kea=None
    if chek_admin and chek_admin['admin']:
        kea=admin_kea
    else:
        kea=markup   
    await bot.send_message(message.chat.id, f"Успешная смена на пользователя {TEST_CURRENT_TG_ID}",reply_markup=kea)

#ПОДКЛЮЧЕНИЕ БОТА И БД
async def main():
    global db_pool
    print("Создаем пул соединений с базой данных...")
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    
    print("Бот вышел в онлайн!")
    await bot.polling(non_stop=True)
if __name__ == '__main__':
    asyncio.run(main())
    asyncio.run(main())