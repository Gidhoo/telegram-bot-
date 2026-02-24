import telebot as tb
from datetime import datetime
from telebot import types
import time
import threading
import io
import requests
import random
import json
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import os

# ====== ПУТЬ К TESSERACT (только если установлен) ======
try:
    if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    pass

# ========== НАСТРОЙКИ ==========
TOKEN = "8529993544:AAEHluimYCHsEmZmMYVVBE7hZpKaR149v88"  # БЕЗ ПРОБЕЛА!
YOUR_CHAT_ID = 1551325264

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)

# Словари для хранения данных
user_message_count = {}
photo_buttons_map = {}
user_data = {}


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def delete_message_after_delay(chat_id, message_id, delay=5):
    """Удаляет сообщение через указанную задержку"""
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass


def compress_image(image_data, quality=70):
    """Сжимает изображение"""
    try:
        img = Image.open(io.BytesIO(image_data))
        output = io.BytesIO()
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"Ошибка сжатия: {e}")
        return image_data


def create_meme_simple(image_data, top_text, bottom_text):
    """Простое создание мема (без сложных шрифтов)"""
    try:
        img = Image.open(io.BytesIO(image_data))
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Используем встроенный шрифт
        font = ImageFont.load_default()

        # Рисуем верхний текст
        if top_text:
            # Получаем размер текста
            bbox = draw.textbbox((0, 0), top_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = 10
            # Рисуем текст с обводкой
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + dx, y + dy), top_text, font=font, fill="black")
            draw.text((x, y), top_text, font=font, fill="white")

        # Рисуем нижний текст
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = height - text_height - 10
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + dx, y + dy), bottom_text, font=font, fill="black")
            draw.text((x, y), bottom_text, font=font, fill="white")

        output = io.BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()
    except Exception as e:
        print(f"Ошибка создания мема: {e}")
        return image_data


def get_currency_rates():
    """Получает курсы валют"""
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        data = response.json()
        usd = data['Valute']['USD']['Value']
        eur = data['Valute']['EUR']['Value']
        return f"💵 USD: {usd:.2f} ₽\n💶 EUR: {eur:.2f} ₽"
    except:
        return "❌ Не удалось получить курсы валют"


def get_random_fact():
    """Случайный факт"""
    facts = [
        "🐝 Пчёлы могут узнавать человеческие лица",
        "🌊 Океан покрывает 71% поверхности Земли",
        "🦒 Жирафы спят всего 2 часа в сутки",
        "🍌 Банан - это ягода",
        "🐙 У осьминога три сердца",
        "❄️ Антарктида - самая большая пустыня в мире",
    ]
    return random.choice(facts)


def get_joke():
    """Случайный анекдот"""
    jokes = [
        "— Дорогой, я решила стать вегетарианкой!\n— Зачем?\n— Чтобы спасти животных!\n— А ты знаешь, сколько растений погибает ради твоего спасения?",
        "Встречаются два программиста:\n— Ты знаешь, я вчера целый день искал себе девушку.\n— Ну и как, нашёл?\n— Нет, зато нашёл 404 ошибку.",
        "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что 31 Oct = 25 Dec",
    ]
    return random.choice(jokes)


def get_weather(city):
    """Получает погоду по городу"""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%w+%h&lang=ru"
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.text.strip():
            return f"🌍 <b>Погода в {city.title()}:</b>\n\n{response.text.strip()}"
        else:
            return f"❌ Город '{city}' не найден"
    except:
        return "❌ Ошибка при получении погоды"


def translate_text(text, dest='en'):
    """Перевод текста через Google Translate"""
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={dest}&dt=t&q={encoded_text}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated = ''
            for sentence in result[0]:
                if sentence and sentence[0]:
                    translated += sentence[0]
            return translated if translated else "❌ Не удалось перевести"
        return "❌ Ошибка перевода"
    except:
        return "❌ Ошибка перевода"


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start', 'main', 'hello'])
def start_command(message):
    user_name = message.from_user.first_name

    # Главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📸 Фото')
    btn2 = types.KeyboardButton('💰 Курсы валют')
    btn3 = types.KeyboardButton('🎲 Факт')
    btn4 = types.KeyboardButton('😄 Анекдот')
    btn5 = types.KeyboardButton('🌤 Погода')
    btn6 = types.KeyboardButton('🔤 Перевод')
    btn7 = types.KeyboardButton('🕐 Время')
    btn8 = types.KeyboardButton('📅 Дата')
    btn9 = types.KeyboardButton('❓ Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)

    welcome_text = f"👋 Привет, {user_name}!\n\nВыбери действие:"

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# ========== ОБРАБОТКА ФОТО ==========

@bot.message_handler(func=lambda message: message.text == '📸 Фото')
def photo_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📤 Отправить фото')
    btn2 = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn1, btn2)

    bot.send_message(message.chat.id, "📸 Отправьте фото:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📤 Отправить фото')
def send_photo_instruction(message):
    bot.send_message(message.chat.id, "📤 Отправьте мне фото")


@bot.message_handler(func=lambda message: message.text == '🔙 Главное меню')
def back_to_main(message):
    start_command(message)


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    # Кнопки для фото
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🎭 Сделать мем', callback_data='meme')
    btn2 = types.InlineKeyboardButton('🗜 Сжать', callback_data='compress')
    btn3 = types.InlineKeyboardButton('🔍 Распознать текст', callback_data='ocr')
    markup.row(btn1, btn2, btn3)

    sent_msg = bot.reply_to(message, '✅ Фото получено! Выберите действие:', reply_markup=markup)

    # Сохраняем связи
    photo_buttons_map[sent_msg.message_id] = {
        'photo_id': message.message_id,
        'buttons_id': sent_msg.message_id,
        'user_id': user_id,
        'user_name': user_name
    }


# ========== ОБРАБОТКА КНОПОК ФОТО ==========

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    try:
        data = photo_buttons_map.get(callback.message.message_id)
        if not data:
            bot.answer_callback_query(callback.id, "❌ Фото не найдено")
            return

        if callback.data == 'meme':
            msg = bot.send_message(callback.message.chat.id,
                                   "📝 Введите текст для мема (верх | низ):\nНапример: Привет | Мир")
            bot.register_next_step_handler(msg, process_meme_text, callback.message)
            bot.answer_callback_query(callback.id)

        elif callback.data == 'compress':
            photo_id = data['photo_id']
            file_info = bot.get_file(photo_id)
            downloaded = bot.download_file(file_info.file_path)
            compressed = compress_image(downloaded)
            bot.send_photo(callback.message.chat.id, compressed, caption="🗜 Сжатое фото")
            bot.answer_callback_query(callback.id, "✅ Готово!")

        elif callback.data == 'ocr':
            photo_id = data['photo_id']
            file_info = bot.get_file(photo_id)
            downloaded = bot.download_file(file_info.file_path)
            try:
                img = Image.open(io.BytesIO(downloaded))
                text = pytesseract.image_to_string(img, lang='rus+eng')
                if text.strip():
                    bot.send_message(callback.message.chat.id, f"📝 Текст:\n\n{text[:1000]}")
                else:
                    bot.send_message(callback.message.chat.id, "😕 Текст не найден")
            except:
                bot.send_message(callback.message.chat.id, "❌ Ошибка распознавания")
            bot.answer_callback_query(callback.id)

    except Exception as e:
        bot.answer_callback_query(callback.id, "❌ Ошибка")
        print(f"Ошибка: {e}")


def process_meme_text(message, original_msg):
    """Создание мема"""
    try:
        text = message.text
        if '|' in text:
            parts = text.split('|', 1)
            top = parts[0].strip()
            bottom = parts[1].strip() if len(parts) > 1 else ''
        else:
            top = text
            bottom = ''

        data = photo_buttons_map.get(original_msg.message_id)
        if not data:
            bot.send_message(message.chat.id, "❌ Фото не найдено")
            return

        photo_id = data['photo_id']
        file_info = bot.get_file(photo_id)
        downloaded = bot.download_file(file_info.file_path)

        meme_data = create_meme_simple(downloaded, top, bottom)
        bot.send_photo(message.chat.id, meme_data, caption="🎉 Мем готов!")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


# ========== ДРУГИЕ КОМАНДЫ ==========

@bot.message_handler(func=lambda message: message.text == '💰 Курсы валют')
def currency_command(message):
    bot.send_message(message.chat.id, get_currency_rates())


@bot.message_handler(func=lambda message: message.text == '🎲 Факт')
def fact_command(message):
    bot.send_message(message.chat.id, get_random_fact())


@bot.message_handler(func=lambda message: message.text == '😄 Анекдот')
def joke_command(message):
    bot.send_message(message.chat.id, get_joke())


@bot.message_handler(func=lambda message: message.text == '🌤 Погода')
def weather_prompt(message):
    msg = bot.send_message(message.chat.id, "🌍 Введите город:")
    bot.register_next_step_handler(msg, process_weather)


def process_weather(message):
    weather = get_weather(message.text.strip())
    bot.send_message(message.chat.id, weather, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔤 Перевод')
def translate_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('🇬🇧 На английский')
    btn2 = types.KeyboardButton('🇷🇺 На русский')
    btn3 = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn1, btn2, btn3)
    msg = bot.send_message(message.chat.id, "🌐 Выберите направление:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_translate_language)


def process_translate_language(message):
    if message.text == '🔙 Главное меню':
        return start_command(message)
    if message.text == '🇬🇧 На английский':
        user_data[message.chat.id] = 'en'
        target = "английский"
    else:
        user_data[message.chat.id] = 'ru'
        target = "русский"
    msg = bot.send_message(message.chat.id, f"📝 Введите текст для перевода на {target}:")
    bot.register_next_step_handler(msg, process_translate_text)


def process_translate_text(message):
    dest = user_data.get(message.chat.id, 'en')
    translated = translate_text(message.text, dest)
    bot.send_message(message.chat.id, f"🔤 <b>Перевод:</b>\n\n{translated}", parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🕐 Время')
def time_command(message):
    bot.send_message(message.chat.id, f"🕐 {datetime.now().strftime('%H:%M:%S')}")


@bot.message_handler(func=lambda message: message.text == '📅 Дата')
def date_command(message):
    bot.send_message(message.chat.id, f"📅 {datetime.now().strftime('%d.%m.%Y')}")


@bot.message_handler(func=lambda message: message.text == '❓ Помощь')
def help_command(message):
    help_text = "🔹 <b>Кнопки:</b>\n\n📸 Фото\n💰 Курсы валют\n🎲 Факт\n😄 Анекдот\n🌤 Погода\n🔤 Перевод\n🕐 Время\n📅 Дата"
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ Бот запущен!")
    print("📱 Токен:", TOKEN[:10] + "...")
    print("=" * 50)

    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)