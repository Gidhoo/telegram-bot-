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
import sys

# ========== НАСТРОЙКИ ==========
TOKEN = "8529993544:AAEHluimYCHsEmZmMYVVBE7hZpKaR149v88"
YOUR_CHAT_ID = 1551325264

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)

# Словари для хранения данных
user_message_count = {}
photo_buttons_map = {}
user_data = {}

# Проверка наличия Tesseract для OCR
TESSERACT_AVAILABLE = False
try:
    if os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        TESSERACT_AVAILABLE = True
except:
    pass


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
    except Exception as e:
        print(f"Ошибка курсов: {e}")
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
        "🦷 Улитки могут спать до 3 лет",
        "🌍 В Австралии живёт больше кенгуру, чем людей",
        "🧠 Мозг человека работает быстрее любого компьютера",
    ]
    return random.choice(facts)


def get_joke():
    """Случайный анекдот"""
    jokes = [
        "— Дорогой, я решила стать вегетарианкой!\n— Зачем?\n— Чтобы спасти животных!\n— А ты знаешь, сколько растений погибает ради твоего спасения?",
        "Встречаются два программиста:\n— Ты знаешь, я вчера целый день искал себе девушку.\n— Ну и как, нашёл?\n— Нет, зато нашёл 404 ошибку.",
        "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что 31 Oct = 25 Dec",
        "Учительница спрашивает Вовочку:\n— Вовочка, почему ты опять опоздал?\n— Марья Ивановна, я спешил в школу, но увидел табличку «Школа — 50 метров» и решил, что успею пройти это расстояние за 50 секунд...",
    ]
    return random.choice(jokes)


def get_weather(city):
    """Получает погоду по городу (ИСПРАВЛЕНО)"""
    try:
        # Очищаем название города
        city = city.strip().lower()
        
        # Используем wttr.in с правильными параметрами
        url = f"https://wttr.in/{city}?format=%c+%t+%w+%h&lang=ru"
        headers = {'User-Agent': 'curl/7.68.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            weather_text = response.text.strip()
            if weather_text and "Unknown" not in weather_text:
                # Парсим ответ
                parts = weather_text.split()
                if len(parts) >= 4:
                    condition = parts[0]
                    temp = parts[1]
                    wind = parts[2]
                    humidity = parts[3]
                    
                    return f"🌍 <b>Погода в {city.title()}</b>\n\n" \
                           f"☁️ {condition}\n" \
                           f"🌡 {temp}\n" \
                           f"💨 Ветер: {wind}\n" \
                           f"💧 Влажность: {humidity}"
            
            return f"🌍 <b>Погода в {city.title()}:</b>\n\n{weather_text}"
        else:
            return f"❌ Город '{city}' не найден"
    except Exception as e:
        print(f"Ошибка погоды: {e}")
        return "❌ Ошибка при получении погоды. Попробуйте другой город."


def translate_text(text, dest='en'):
    """Перевод текста через Google Translate (ИСПРАВЛЕНО)"""
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
            
            if translated:
                return translated
            else:
                return "❌ Не удалось перевести текст"
        else:
            return "❌ Ошибка сервиса перевода"
    except requests.exceptions.Timeout:
        return "❌ Превышено время ожидания"
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return "❌ Ошибка перевода. Попробуйте позже."


def generate_callsign(word):
    """Генерирует позывной на основе одного слова (НОВАЯ ФУНКЦИЯ)"""
    
    # База приставок для позывных
    prefixes = ["Тихий", "Быстрый", "Дикий", "Мудрый", "Хитрый", 
                "Смелый", "Вольный", "Ярый", "Вещий", "Рыжий",
                "Северный", "Южный", "Западный", "Восточный", "Стальной",
                "Огненный", "Ледяной", "Грозовой", "Солнечный", "Лунный"]
    
    # База суффиксов для позывных
    suffixes = ["Волк", "Лис", "Медведь", "Орёл", "Сокол", 
                "Барс", "Рысь", "Тигр", "Лев", "Ворон",
                "Шторм", "Ветер", "Гром", "Молния", "Туча",
                "Коготь", "Клык", "Меч", "Щит", "Копьё"]
    
    # Очищаем входное слово
    word = word.strip().lower()
    
    # Генерируем случайные варианты
    results = []
    
    # Вариант 1: Приставка + слово
    prefix = random.choice(prefixes)
    results.append(f"🎖 {prefix} {word.title()}")
    
    # Вариант 2: слово + суффикс
    suffix = random.choice(suffixes)
    results.append(f"🎖 {word.title()} {suffix}")
    
    # Вариант 3: Приставка + суффикс (без слова)
    results.append(f"🎖 {random.choice(prefixes)} {random.choice(suffixes)}")
    
    # Вариант 4: слово в другом падеже
    if word.endswith('а') or word.endswith('я'):
        word_mod = word[:-1] + 'ая'
    elif word.endswith('ок'):
        word_mod = word[:-2] + 'очный'
    else:
        word_mod = word + 'ный'
    
    results.append(f"🎖 {random.choice(prefixes)} {word_mod.title()}")
    
    return results


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
    btn10 = types.KeyboardButton('🎯 Позывной')  # НОВАЯ КНОПКА
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10)

    welcome_text = f"👋 Привет, {user_name}!\n\n"
    welcome_text += "Я многофункциональный бот. Выбери действие:\n\n"
    welcome_text += "📸 Работа с фото (мемы, сжатие, текст)\n"
    welcome_text += "💰 Курсы валют USD/EUR\n"
    welcome_text += "🎲 Случайные факты\n"
    welcome_text += "😄 Анекдоты\n"
    welcome_text += "🌤 Погода в любом городе\n"
    welcome_text += "🔤 Перевод текста\n"
    welcome_text += "🕐 Текущее время\n"
    welcome_text += "📅 Текущая дата\n"
    welcome_text += "🎯 Генератор позывных по слову"

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# ========== НОВАЯ КОМАНДА - ГЕНЕРАТОР ПОЗЫВНЫХ ==========

@bot.message_handler(func=lambda message: message.text == '🎯 Позывной')
def callsign_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎯 <b>Генератор позывных</b>\n\n"
                          "Напиши одно слово (например: волк, космос, гроза, ночь),\n"
                          "а я придумаю уникальные позывные!",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_callsign)


def process_callsign(message):
    try:
        word = message.text.strip()
        
        # Проверка на пустой ввод
        if not word:
            bot.send_message(message.chat.id, "❌ Напиши хотя бы одно слово!")
            return
        
        # Проверка на длину
        if len(word) > 20:
            bot.send_message(message.chat.id, "❌ Слишком длинное слово! Максимум 20 символов.")
            return
        
        # Генерируем позывные
        results = generate_callsign(word)
        
        # Формируем ответ
        response = f"🎯 <b>Позывные для слова '{word.title()}':</b>\n\n"
        for i, result in enumerate(results, 1):
            response += f"{result}\n"
        
        response += "\n✨ Выбери тот, который больше нравится!"
        
        bot.send_message(message.chat.id, response, parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


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
    bot.send_message(message.chat.id, "📤 Отправьте мне фото (как изображение, не файл)")


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


@bot.message_handler(content_types=['document'])
def get_document(message):
    if message.document.mime_type.startswith('image/'):
        bot.reply_to(message, "📸 Пожалуйста, отправьте фото как изображение, а не файл")
    else:
        bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте фото")


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
                                   "📝 Введите текст для мема в формате:\n"
                                   "верхний текст | нижний текст\n"
                                   "Например: Привет | Мир")
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
            if not TESSERACT_AVAILABLE:
                bot.send_message(callback.message.chat.id, "❌ Распознавание текста временно недоступно")
                bot.answer_callback_query(callback.id)
                return
                
            photo_id = data['photo_id']
            file_info = bot.get_file(photo_id)
            downloaded = bot.download_file(file_info.file_path)
            try:
                img = Image.open(io.BytesIO(downloaded))
                text = pytesseract.image_to_string(img, lang='rus+eng')
                if text.strip():
                    # Обрезаем если слишком длинный
                    if len(text) > 1000:
                        text = text[:1000] + "...\n(текст обрезан)"
                    bot.send_message(callback.message.chat.id, f"📝 <b>Распознанный текст:</b>\n\n{text}", parse_mode='HTML')
                else:
                    bot.send_message(callback.message.chat.id, "😕 Не удалось распознать текст на фото")
            except Exception as e:
                bot.send_message(callback.message.chat.id, "❌ Ошибка распознавания")
                print(f"Ошибка OCR: {e}")
            bot.answer_callback_query(callback.id)

    except Exception as e:
        bot.answer_callback_query(callback.id, "❌ Ошибка")
        print(f"Ошибка в callback: {e}")


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

        # Удаляем сообщение с запросом текста
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        print(f"Ошибка создания мема: {e}")


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
    msg = bot.send_message(message.chat.id, 
                          "🌍 <b>Погода</b>\n\n"
                          "Введите название города (например: Москва, Лондон, Париж):",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_weather)


def process_weather(message):
    city = message.text.strip()
    
    # Отправляем сообщение о загрузке
    waiting = bot.send_message(message.chat.id, "⏳ Получаю данные о погоде...")
    
    # Получаем погоду
    weather = get_weather(city)
    
    # Удаляем сообщение о загрузке
    try:
        bot.delete_message(message.chat.id, waiting.message_id)
    except:
        pass
    
    # Отправляем результат
    bot.send_message(message.chat.id, weather, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔤 Перевод')
def translate_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('🇬🇧 На английский')
    btn2 = types.KeyboardButton('🇷🇺 На русский')
    btn3 = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn1, btn2, btn3)
    
    msg = bot.send_message(message.chat.id, 
                          "🌐 <b>Переводчик</b>\n\n"
                          "Выберите направление перевода:",
                          parse_mode='HTML',
                          reply_markup=markup)
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
    
    msg = bot.send_message(message.chat.id, 
                          f"📝 Введите текст для перевода на <b>{target}</b> язык:",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_translate_text)


def process_translate_text(message):
    try:
        dest = user_data.get(message.chat.id, 'en')
        
        # Отправляем сообщение о загрузке
        waiting = bot.send_message(message.chat.id, "⏳ Перевожу...")
        
        # Переводим
        translated = translate_text(message.text, dest)
        
        # Удаляем сообщение о загрузке
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except:
            pass
        
        # Отправляем результат
        bot.send_message(message.chat.id, f"🔤 <b>Перевод:</b>\n\n{translated}", parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


@bot.message_handler(func=lambda message: message.text == '🕐 Время')
def time_command(message):
    current_time = datetime.now().strftime('%H:%M:%S')
    bot.send_message(message.chat.id, f"🕐 <b>Текущее время:</b> {current_time}", parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '📅 Дата')
def date_command(message):
    current_date = datetime.now().strftime('%d.%m.%Y')
    bot.send_message(message.chat.id, f"📅 <b>Текущая дата:</b> {current_date}", parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '❓ Помощь')
def help_command(message):
    help_text = "🔹 <b>Как пользоваться ботом:</b>\n\n"
    help_text += "📸 <b>Фото:</b> отправь фото и используй кнопки:\n"
    help_text += "   • 🎭 Сделать мем - наложить текст\n"
    help_text += "   • 🗜 Сжать - уменьшить размер\n"
    help_text += "   • 🔍 Распознать текст - OCR\n\n"
    help_text += "💰 <b>Курсы валют:</b> USD и EUR\n"
    help_text += "🎲 <b>Факт:</b> случайный интересный факт\n"
    help_text += "😄 <b>Анекдот:</b> поднять настроение\n"
    help_text += "🌤 <b>Погода:</b> погода в любом городе\n"
    help_text += "🔤 <b>Перевод:</b> перевод текста\n"
    help_text += "🎯 <b>Позывной:</b> генератор уникальных позывных\n"
    help_text += "🕐 <b>Время:</b> текущее время\n"
    help_text += "📅 <b>Дата:</b> текущая дата"

    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower()
    
    if text in ['спасибо', 'спс', 'благодарю']:
        bot.send_message(message.chat.id, "🙏 Пожалуйста! Рад помочь!")
    elif text == 'привет':
        bot.send_message(message.chat.id, f"👋 Привет, {message.from_user.first_name}!")
    elif text == 'id':
        bot.send_message(message.chat.id, f"🆔 Ваш ID: {message.from_user.id}")
    elif text == 'пока':
        bot.send_message(message.chat.id, "👋 До встречи!")
    elif text == 'бот':
        bot.send_message(message.chat.id, "🤖 Я здесь!")


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("📱 Версия: 4.0 (Погода исправлена + Позывные)")
    print("📱 Токен:", TOKEN[:10] + "...")
    print("=" * 50)
    print("📋 Доступные команды:")
    print("   • /start - главное меню")
    print("   • 📸 Фото - работа с изображениями")
    print("   • 🎯 Позывной - генератор позывных")
    print("   • 🌤 Погода - погода в любом городе")
    print("   • 🔤 Перевод - перевод текста")
    print("=" * 50)
    print("🔄 Бот работает в бесконечном цикле...")
    print("=" * 50)

    # Бесконечный цикл с перезапуском при ошибке
    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
