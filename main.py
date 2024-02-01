import requests
import json
import telegram
import asyncio
from PIL import Image

import setting
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Замените 'YourTelegramBotToken' на ваш токен бота в Telegram
bot_token = setting.bot_token
bot_chatID = setting.bot_chatID

# Замените ['YourVKGroupID1', 'YourVKGroupID2'] на список ID ваших групп Вконтакте
vk_group_ids = setting.vk_group_ids
vk_access_token = setting.vk_access_token

# Функция для отправки сообщения с изображением и кнопками в группу в Telegram
async def send_message_with_image(message, image, group_id):
    bot = telegram.Bot(token=bot_token)

    if image is not None:
        keyboard = [
            [
                InlineKeyboardButton("Опубликовать", callback_data=f"publish_{group_id}"),
                InlineKeyboardButton("Игнорировать", callback_data="ignore")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_photo(chat_id=bot_chatID, photo=image, caption=message, reply_markup=reply_markup)
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

# Функция для публикации поста в группе Вконтакте
def publish_post(group_id, text):
    # Код для публикации поста в группе Вконтакте
    # Используйте API Вконтакте или библиотеку VK API для публикации постов
    # Пример:
    # url = f'https://api.vk.com/method/wall.post?owner_id=-{group_id}&message={text}&access_token={vk_access_token}&v=5.131'
    # response = requests.get(url)
    # ...
    pass

# Отслеживание новых постов и отправка их в группу Telegram
async def track_new_posts():
    last_post_ids = {group_id: 0 for group_id in vk_group_ids}
    bot = telegram.Bot(token=bot_token)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('publish_'))
    def handle_publish_button_click(call):
        group_id = call.data.split('_')[1]
        text = call.message.caption

        publish_post(group_id, text)
    
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
                            await send_message_with_image(message, image, group_id)
                        else:
                            message = f"Новый пост в группе Вконтакте! https://vk.com/public{group_id} \n\n{text}"
                            await send_message_with_image(message, None, group_id)
                    
                    last_post_ids[group_id] = post['id']
        
        await asyncio.sleep(60)

asyncio.run(track_new_posts())
