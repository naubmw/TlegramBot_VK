import requests
import json
import telegram
import asyncio
from PIL import Image
import setting

# Замените 'YourTelegramBotToken' на ваш токен бота в Telegram
bot_token = setting.bot_token
bot_chatID = setting.bot_chatID

# Замените 'YourVKGroupID' на ID вашей группы Вконтакте
vk_group_id = setting.vk_group_id
vk_access_token = setting.vk_access_token

# Функция для отправки сообщения с изображением в группу в Telegram
async def send_message_with_image(message, image):
    bot = telegram.Bot(token=bot_token)
    await bot.send_photo(chat_id=bot_chatID, photo=image, caption=message)

# Получение информации о последних постах в группе Вконтакте
def get_latest_posts():
    url = f'https://api.vk.com/method/wall.get?owner_id=-{vk_group_id}&count=5&access_token={vk_access_token}&v=5.131'
    response = requests.get(url)
    print(response)
    
    data = json.loads(response.text)
    
    if 'response' in data:
        posts = data['response']['items']
        return posts
    else:
        return []

# Загрузка изображения из Вконтакте
def download_image(url):
    response = requests.get(url)
    image = response.content
    return image

# Отслеживание новых постов и отправка их в группу Telegram
async def track_new_posts():
    last_post_id = 0
    
    while True:
        posts = get_latest_posts()
        
        for post in posts:
            if post['id'] > last_post_id:
                text = post['text']
                
                if 'attachments' in post:
                    attachments = post['attachments']
                    link = None
                    
                    for attachment in attachments:
                        if attachment['type'] == 'photo':
                            sizes = attachment['photo']['sizes']
                            link = max(sizes, key=lambda x: x['width'])['url']
                            break
                    
                    if link:
                        image = download_image(link)
        # Пауза в 1 минуту перед следующей проверкой
                        message = f"Новый пост в группе Вконтакте! https://vk.com/public217414089\n\n{text}"
                        await send_message_with_image(message, image)
                    else:
                        message = f"Новый пост в группе Вконтакте! https://vk.com/public217414089 \n\n{text}"
                        await send_message_with_image(message, image)
                
                last_post_id = post['id']
        
        # Пауза в 1 минуту перед следующей проверкой
        await asyncio.sleep(60)

asyncio.run(track_new_posts())