import telebot
import ollama
import sqlite3
import re
import os
from dotenv import load_dotenv
import requests
from telebot import types

# Load environment variables

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram bot configuration

bot = telebot.TeleBot(BOT_TOKEN)
OLLAMA_MODEL = 'mobile_sales_bot'

# In-memory user session storage

user_histories = {}
user_contacts = {}

# Database connection

conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()

# Create orders table if it does not exist

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        phone TEXT,
        email TEXT
    )
''')

conn.commit()


# Search smartphone image using SerpAPI

def get_image_url(query):

    try:

        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google_images",
            "q": f"{query} smartphone product photo white background",
            "api_key": os.getenv("SERPAPI_KEY")
        }

        res = requests.get(
            url,
            params=params,
            timeout=10
        ).json()

        images = res.get("images_results", [])

        for img in images:

            img_url = img.get("original")

            if img_url and img_url.startswith("http"):
                return img_url

    except Exception as e:
        print(f"SerpAPI error: {e}")

    return "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=600"


# Save order to database

def save_order(chat_id, phone, email):

    cursor.execute(
        'INSERT INTO orders (chat_id, phone, email) VALUES (?, ?, ?)',
        (chat_id, phone, email)
    )

    conn.commit()


# Main menu keyboard

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    btn1 = types.KeyboardButton("📱 Каталог")
    btn2 = types.KeyboardButton("🔍 Поиск телефона")
    btn3 = types.KeyboardButton("🛒 Оформить заказ")

    markup.add(btn1, btn2)
    markup.add(btn3)

    return markup


# Menu after successful order

def after_order_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    btn1 = types.KeyboardButton("🔄 Вернуться в каталог")
    btn2 = types.KeyboardButton("🔍 Найти другой телефон")

    markup.add(btn1, btn2)

    return markup


# Start command handler

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

    chat_id = message.chat.id

    user_histories[chat_id] = []

    user_contacts[chat_id] = {
        'phone': None,
        'email': None
    }

    bot.send_message(
        chat_id,
        "Привет! Добро пожаловать в магазин смартфонов 📱",
        reply_markup=main_menu()
    )


# Main message handler

@bot.message_handler(func=lambda message: True)
def handle_message(message):

    chat_id = message.chat.id
    text = message.text

    # Handle menu buttons

    if text == "📱 Каталог":

        bot.send_message(
            chat_id,
            "Доступные бренды:\n\n• iPhone\n• Samsung\n• Google Pixel",
            reply_markup=main_menu()
        )

        return

    elif text == "🔍 Поиск телефона":

        bot.send_message(
            chat_id,
            "Введите модель телефона.\n\nНапример:\n• iPhone 14 Pro Max\n• Samsung Galaxy S24",
            reply_markup=main_menu()
        )

        return

    elif text == "🛒 Оформить заказ":

        bot.send_message(
            chat_id,
            "Введите номер телефона и Email одним сообщением.\n\nНапример:\n+49123456789 test@gmail.com",
            reply_markup=main_menu()
        )

        return

    elif text == "🔄 Вернуться в каталог":

        bot.send_message(
            chat_id,
            "Снова открываем каталог 📱",
            reply_markup=main_menu()
        )

        return

    elif text == "🔍 Найти другой телефон":

        bot.send_message(
            chat_id,
            "Введите название другого телефона 📲",
            reply_markup=main_menu()
        )

        return

    # Initialize user session

    if chat_id not in user_histories:
        user_histories[chat_id] = []

    if chat_id not in user_contacts:

        user_contacts[chat_id] = {
            'phone': None,
            'email': None
        }

    # Validate email and phone number

    email_match = re.search(
        r'\S+@\S+\.\S+',
        text
    )

    if email_match:
        user_contacts[chat_id]['email'] = email_match.group(0)

    digits = re.sub(r'\D', '', text)

    if len(digits) >= 10:
        user_contacts[chat_id]['phone'] = digits

    # Save user message to conversation history

    user_histories[chat_id].append({
        'role': 'user',
        'content': text
    })

    # Send request to Ollama model

    try:

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=user_histories[chat_id][-10:],
            options={
                'num_predict': 250,
                'temperature': 0.4
            }
        )

        bot_reply = response['message']['content']

        # Detect smartphone model for image search

        model_to_search = None

        tag_match = re.search(
            r'\[(?:IMG_SEARCH:\s*)?(.*?)\]',
            bot_reply
        )

        if tag_match:

            model_to_search = tag_match.group(1)

        else:

            brand_match = re.search(
                r'(iPhone \d+|Samsung \S+|Pixel \d+)',
                bot_reply,
                re.I
            )

            if brand_match:
                model_to_search = brand_match.group(0)

        # Remove service tags from model response

        clean_text = re.sub(
            r'\[IMG_SEARCH:.*?\]',
            '',
            bot_reply
        )

        clean_text = clean_text.replace(
            "КОНТАКТЫ_ПОЛУЧЕНЫ",
            ""
        ).strip()

        # Send text response to user

        bot.send_message(
            chat_id,
            clean_text,
            reply_markup=main_menu()
        )

        # Send smartphone image

        if model_to_search:

            bot.send_chat_action(
                chat_id,
                'upload_photo'
            )

            img_url = get_image_url(model_to_search)

            if img_url:

                try:

                    bot.send_photo(
                        chat_id,
                        img_url,
                        caption=f"Вот как выглядит {model_to_search}",
                        timeout=10,
                        reply_markup=main_menu()
                    )

                except Exception as photo_err:

                    print(f"Photo upload error: {photo_err}")

                    bot.send_message(
                        chat_id,
                        "📸 Не удалось загрузить фото, но модель отличная!",
                        reply_markup=main_menu()
                    )

        # Save completed order

        if "КОНТАКТЫ_ПОЛУЧЕНЫ" in bot_reply:

            phone = user_contacts[chat_id]['phone']
            email = user_contacts[chat_id]['email']

            if phone and email:

                save_order(chat_id, phone, email)

                bot.send_message(
                    chat_id,
                    "✅ Заказ оформлен! Мы свяжемся с вами.",
                    reply_markup=after_order_menu()
                )

                user_contacts[chat_id] = {
                    'phone': None,
                    'email': None
                }

        # Save assistant response to history

        user_histories[chat_id].append({
            'role': 'assistant',
            'content': clean_text
        })

    # Error handling

    except Exception as e:

        print(f"Error: {e}")

        bot.send_message(
            chat_id,
            "Упс, я запутался. Попробуйте еще раз!",
            reply_markup=main_menu()
        )


# Start bot polling

if __name__ == '__main__':

    print("Бот запущен 🚀")

    bot.infinity_polling()