import requests
import json
import telegram
import asyncio
from PIL import Image
import setting

# Замените 'YourTelegramBotToken' на ваш токен бота в Telegram
bot_token = setting.bot_token
bot_chatID = setting.bot_chatID

# Замените ['YourVKGroupID1', 'YourVKGroupID2'] на список ID ваших групп Вконтакте
vk_group_ids = setting.vk_group_ids
vk_access_token = setting.vk_access_token
print(1)

# Функция для отправки сообщения с изображением в группу в Telegram
async def send_message_with_image(message, image):
    bot = telegram.Bot(token=bot_token)
    
    if image is not None:
        await bot.send_photo(chat_id=bot_chatID, photo=image, caption=message)
    else:
        await bot.send_message(chat_id=bot_chatID, text=message)

# Получение информации о последних постах в группе Вконтакте
def get_latest_posts(group_id):
    url = f'https://api.vk.com/method/wall.get?owner_id=-{group_id}&count=5&access_token={vk_access_token}&v=5.131'
    response = requests.get(url)
    
    data = json.loads(response.text)
    
    if 'response' in data:
        posts = data['response']['items']
        return posts
    else:
        return []

# Загрузка изображения из Вконтакте
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        image = response.content
        return image
    else:
        return None

# Отслеживание новых постов и отправка их в группу Telegram
async def track_new_posts():
    last_post_ids = {group_id: 0 for group_id in vk_group_ids}
    
    while True:
        for group_id in vk_group_ids:
            posts = get_latest_posts(group_id)
            
            for post in posts:
                if post['id'] > last_post_ids[group_id]:
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
                            message = f"Новый пост в группе Вконтакте! https://vk.com/public{group_id}\n\n{text}"
                            await send_message_with_image(message, image)
                        else:
                            message = f"Новый пост в группе Вконтакте! https://vk.com/public{group_id} \n\n{text}"
                            await send_message_with_image(message, None)
                    
                    last_post_ids[group_id] = post['id']
        
        await asyncio.sleep(60)

asyncio.run(track_new_posts())
