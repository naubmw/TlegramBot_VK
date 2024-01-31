import requests
import json
import telegram
import asyncio
import setting

# Замените 'YourTelegramBotToken' на ваш токен бота в Telegram
bot_token = setting.bot_token
bot_chatID = setting.bot_chatID

# Замените 'YourVKGroupID' на ID вашей группы Вконтакте
vk_group_id = setting.vk_group_id
vk_access_token = setting.vk_access_token

# Функция для отправки сообщения в группу в Telegram
async def send_message(message):
    bot = telegram.Bot(token=bot_token)
    await bot.sendMessage(chat_id=bot_chatID, text=message)

# Получение информации о последних постах в группе Вконтакте
def get_latest_posts():
    url = f'https://api.vk.com/method/wall.get?owner_id=-{vk_group_id}&count=5&access_token={vk_access_token}&v=5.131'
    response = requests.get(url)
    data = json.loads(response.text)
    
    if 'response' in data:
        posts = data['response']['items']
        return posts
    else:
        return []

# Отслеживание новых постов и отправка их в группу Telegram
async def track_new_posts():
    last_post_id = 0
    
    while True:
        posts = get_latest_posts()
        
        for post in posts:
            if post['id'] > last_post_id:
                message = f"Новый пост в группе Вконтакте!\n\n{post['text']}"
                await send_message(message)
                last_post_id = post['id']
        
        # Пауза в 1 минуту перед следующей проверкой
        await asyncio.sleep(60)

asyncio.run(track_new_posts())

