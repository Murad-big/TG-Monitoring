from pyrogram import Client, filters

import asyncio
import json
#Загружаем config для работы
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()
# Укажите свои API ID и API Hash для подключения к Telegram API
proxy = config["proxy"] if "proxy" in config and config["proxy"]["enabled"] else None
proxy_dict = None
# if proxy не пустой то заполняем, это сделано для вас, чтоб вы могли использовать код и без прокси
if proxy:
    proxy_dict = dict(
        scheme=proxy["type"],
        hostname=proxy["hostname"],
        port=proxy["port"],
        username=proxy.get("username"),  # .get() используется для обработки необязательных полей
        password=proxy.get("password")
    )
#Это для pyrogram
app = Client(
    "my_session",
    api_id=config["api_id"],
    api_hash=config["api_hash"],
    proxy=proxy_dict
)

async def check_message(client, message):
    my_username = config["username"] #это чтоб не перехватывать ваши сообщения
    if message.from_user.id in config["id_users"]: #проверка перехвата, если это ваше сообщение, то не взаимодействуем
        return
    print(f"Новое сообщение из {message.chat.title}: {message.text}")  # Вывод каждого нового сообщения в консоль
    chat_link = f"https://t.me/{message.chat.username}" if message.chat.username else "Приватный чат"
    sender = f"@{message.from_user.username}" if message.from_user.username else "Неизвестный отправитель"
    text = f"Чат: {chat_link}\nОтправитель: {sender}\nСообщение полностью: {message.text}"
    print(text)
    date = message.date
    message_data = {
        "group_name": message.chat.title,
        "absender": message.from_user.username,
        "id_user": message.from_user.id,
        "id_message": message.id,
        "id_group": message.chat.id,
        "date": date.isoformat(), # тут я делаю из class datetime в str, а то json выдаст ошибку
        "text": message.text
    }


    # Записываем данные в файл JSON
    with open('messages.json', 'a', encoding='utf-8') as file:
        json.dump(message_data, file, indent=4, ensure_ascii=False)
        file.write("\n")

    # пересылка сообщения в вашу группу
    if message.chat.username:
        await client.send_message(my_username, f"Вам пришло сообщение от @{message.chat.username}")
    else:
        await client.send_message(my_username, f"Вам пришло сообщение от чата: {message.chat.title} ")
    await client.forward_messages(my_username,from_chat_id=message.chat.id,message_ids=message.id)


@app.on_message(filters.all)
async def message_handler(client, message):
    await check_message(client, message)


# Запускаем клиента Pyrogram
app.run()