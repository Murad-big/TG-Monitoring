from pyrogram import Client, filters
import asyncio
import json


def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)


config = load_config()

proxy = config.get("proxy") if "proxy" in config else None
proxy_dict = None

if proxy and proxy.get("enabled"):
    proxy_dict = {
        "scheme": proxy["type"],
        "hostname": proxy["hostname"],
        "port": proxy["port"],
        "username": proxy.get("username"), 
        "password": proxy.get("password")
    }

app = Client(
    "my_session",
    api_id=config["api_id"],
    api_hash=config["api_hash"],
    proxy=proxy_dict
)


async def check_message(client, message):
    my_username = config["username"] 
    if message.from_user.id in config["id_users"]: 
        return

    print(f"Новое сообщение из {message.chat.title}: {message.text}")  
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
        "date": date.isoformat(),  
        "text": message.text
    }

    with open('messages.json', 'a', encoding='utf-8') as file:
        json.dump(message_data, file, indent=4, ensure_ascii=False)
        file.write("\n")

    if message.chat.username:
        await client.send_message(my_username, f"Вам пришло сообщение от @{message.chat.username}")
    else:
        await client.send_message(my_username, f"Вам пришло сообщение от чата: {message.chat.title}")
    
    await client.forward_messages(my_username, from_chat_id=message.chat.id, message_ids=message.id)


@app.on_message(filters.all)
async def message_handler(client, message):
    await check_message(client, message)


app.run()
