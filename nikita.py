import telebot as tb
from datetime import datetime
from telebot import types
import time
import requests
import random
import urllib.parse
import io
import os
from PIL import Image, ImageDraw, ImageFont

# ========== НАСТРОЙКИ ==========
TOKEN = "8529993544:AAEHluimYCHsEmZmMYVVBE7hZpKaR149v88"
YOUR_CHAT_ID = 1551325264
DEEPSEEK_KEY = "sk-d838f69da7794f3998464fd7ead477b9"

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)
user_data = {}
photo_buttons_map = {}


# ========== DEEPSEEK AI (КАК Я) ==========

def ask_deepseek(question):
    """Спрашивает DeepSeek и получает ответ"""
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_KEY}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Ты полезный AI-ассистент. Отвечай подробно, дружелюбно и с эмодзи."},
                {"role": "user", "content": question}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"❌ Ошибка API: {response.status_code}"
            
    except Exception as e:
        return f"❌ Ошибка: {e}"


# ========== ГЕНЕРАЦИЯ КАРТИНОК ==========

def create_image(prompt):
    """Создаёт картинку по описанию"""
    try:
        # Кодируем текст для URL
        encoded = urllib.parse.quote(prompt)
        
        # Используем бесплатный API Pollinations
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        params = {
            "width": 1024,
            "height": 1024,
            "nologo": "true",
            "model": "flux"
        }
        
        response = requests.get(url, params=params, timeout=45)
        
        if response.status_code == 200:
            return response.content
        else:
            return None
            
    except Exception as e:
        print(f"Ошибка создания картинки: {e}")
        return None


# ========== КУРСЫ ВАЛЮТ (ОНЛАЙН) ==========

def get_currency():
    """Получает актуальные курсы валют"""
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            usd = data['Valute']['USD']['Value']
            eur = data['Valute']['EUR']['Value']
            cny = data['Valute']['CNY']['Value']
            
            text = "💰 <b>Курсы валют ЦБ РФ</b>\n\n"
            text += f"🇺🇸 USD: <b>{usd:.2f} ₽</b>\n"
            text += f"🇪🇺 EUR: <b>{eur:.2f} ₽</b>\n"
            text += f"🇨🇳 CNY: <b>{cny:.2f} ₽</b>\n\n"
            text += f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            return text
        else:
            return "❌ Не удалось получить курсы"
            
    except Exception as e:
        return f"❌ Ошибка: {e}"


# ========== ПОГОДА ==========

def get_weather(city):
    """Получает погоду в городе"""
    try:
        # Получаем координаты города
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        
        if geo_response.status_code != 200:
            return f"❌ Город '{city}' не найден"
        
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return f"❌ Город '{city}' не найден"
        
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        city_name = geo_data['results'][0]['name']
        country = geo_data['results'][0].get('country', '')
        
        # Получаем погоду
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m&timezone=auto"
        weather_response = requests.get(weather_url, timeout=5)
        
        if weather_response.status_code != 200:
            return f"❌ Не удалось получить погоду"
        
        weather_data = weather_response.json()
        current = weather_data['current_weather']
        temp = current['temperature']
        wind = current['windspeed']
        
        # Определяем погоду
        if temp > 20:
            condition = "☀️ Солнечно"
        elif temp > 10:
            condition = "⛅ Облачно"
        elif temp > 0:
            condition = "☁️ Пасмурно"
        else:
            condition = "❄️ Холодно"
        
        text = f"🌍 <b>{city_name}, {country}</b>\n\n"
        text += f"🌡 Температура: <b>{temp}°C</b>\n"
        text += f"☁️ {condition}\n"
        text += f"💨 Ветер: <b>{wind} км/ч</b>"
        
        return text
        
    except Exception as e:
        return f"❌ Ошибка: {e}"


# ========== ПЕРЕВОД ==========

def translate(text, dest='en'):
    """Переводит текст"""
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={dest}&dt=t&q={encoded}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            translated = ''
            for sentence in result[0]:
                if sentence and sentence[0]:
                    translated += sentence[0]
            return translated
        else:
            return "❌ Ошибка перевода"
    except:
        return "❌ Ошибка перевода"


# ========== ФИЛЬМ ПО НАСТРОЕНИЮ ==========

def get_movie(mood):
    """Рекомендует фильм по настроению"""
    movies = {
        "веселый": "🎬 1+1 (2011) - Французская комедия",
        "грустный": "🎬 Побег из Шоушенка (1994) - Драма",
        "романтичный": "🎬 500 дней лета (2009) - Романтика",
        "страшный": "🎬 Заклятие (2013) - Ужасы",
        "фантастика": "🎬 Начало (2010) - Фантастика",
    }
    
    mood = mood.lower()
    for key in movies:
        if key in mood:
            return movies[key]
    
    return "🎬 1+1 (2011) - Отличный фильм для любого настроения!"


# ========== ПОЗЫВНОЙ ==========

def get_callsign(word):
    """Генерирует позывной"""
    prefixes = ["Тихий", "Быстрый", "Дикий", "Мудрый", "Смелый"]
    suffixes = ["Волк", "Лис", "Медведь", "Орёл", "Сокол"]
    
    results = []
    results.append(f"🎖 {random.choice(prefixes)} {word.title()}")
    results.append(f"🎖 {word.title()} {random.choice(suffixes)}")
    results.append(f"🎖 {random.choice(prefixes)} {random.choice(suffixes)}")
    
    return results


# ========== ФУНКЦИИ ДЛЯ ФОТО ==========

def create_meme(image_data, top, bottom):
    """Создаёт мем из фото"""
    try:
        img = Image.open(io.BytesIO(image_data))
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        font = ImageFont.load_default()
        
        if top:
            bbox = draw.textbbox((0, 0), top, font=font)
            x = (width - (bbox[2] - bbox[0])) // 2
            y = 10
            draw.text((x, y), top, font=font, fill="white")
        
        if bottom:
            bbox = draw.textbbox((0, 0), bottom, font=font)
            x = (width - (bbox[2] - bbox[0])) // 2
            y = height - (bbox[3] - bbox[1]) - 10
            draw.text((x, y), bottom, font=font, fill="white")
        
        output = io.BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()
    except:
        return image_data


def compress_image(image_data):
    """Сжимает изображение"""
    try:
        img = Image.open(io.BytesIO(image_data))
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True)
        return output.getvalue()
    except:
        return image_data


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Кнопки
    btn1 = types.KeyboardButton('🤖 Спросить DeepSeek')
    btn2 = types.KeyboardButton('🎨 Создать картинку')
    btn3 = types.KeyboardButton('🎬 Фильм по настроению')
    btn4 = types.KeyboardButton('📸 Отправить фото')
    btn5 = types.KeyboardButton('💰 Курсы валют')
    btn6 = types.KeyboardButton('🌤 Погода')
    btn7 = types.KeyboardButton('🔤 Перевод')
    btn8 = types.KeyboardButton('🎯 Позывной')
    btn9 = types.KeyboardButton('❓ Помощь')
    
    markup.add(btn1, btn2, btn3)
    markup.add(btn4)
    markup.add(btn5, btn6, btn7, btn8, btn9)
    
    text = f"👋 Привет, {message.from_user.first_name}!\n\n"
    text += "🤖 DeepSeek - задай любой вопрос\n"
    text += "🎨 Картинка - создай изображение\n"
    text += "🎬 Фильм - по настроению\n"
    text += "📸 Фото - мемы и сжатие\n"
    text += "💰 Курсы - онлайн валют"
    
    bot.send_message(message.chat.id, text, reply_markup=markup)


# ========== DEEPSEEK ==========

@bot.message_handler(func=lambda m: m.text == '🤖 Спросить DeepSeek')
def deepseek_prompt(m):
    msg = bot.send_message(m.chat.id, "🤖 Задай вопрос:")
    bot.register_next_step_handler(msg, deepseek_answer)


def deepseek_answer(m):
    wait = bot.send_message(m.chat.id, "⏳ Думаю...")
    answer = ask_deepseek(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, answer)


# ========== ГЕНЕРАЦИЯ КАРТИНОК ==========

@bot.message_handler(func=lambda m: m.text == '🎨 Создать картинку')
def image_prompt(m):
    msg = bot.send_message(m.chat.id, "🎨 Опиши картинку:")
    bot.register_next_step_handler(msg, create_image_handler)


def create_image_handler(m):
    wait = bot.send_message(m.chat.id, "🎨 Создаю картинку... (до 30 сек)")
    image = create_image(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    
    if image:
        bot.send_photo(m.chat.id, image, caption=f"🎨 {m.text}")
    else:
        bot.send_message(m.chat.id, "❌ Не удалось создать картинку")


# ========== ФИЛЬМ ==========

@bot.message_handler(func=lambda m: m.text == '🎬 Фильм по настроению')
def movie_prompt(m):
    msg = bot.send_message(m.chat.id, "🎬 Какое настроение?")
    bot.register_next_step_handler(msg, movie_answer)


def movie_answer(m):
    movie = get_movie(m.text)
    bot.send_message(m.chat.id, movie)


# ========== ФОТО ==========

@bot.message_handler(func=lambda m: m.text == '📸 Отправить фото')
def photo_instruction(m):
    bot.send_message(m.chat.id, "📸 Отправь фото:")


@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('🎭 Мем', callback_data='meme'),
        types.InlineKeyboardButton('🗜 Сжать', callback_data='compress')
    )
    
    sent = bot.reply_to(m, "✅ Что сделать с фото?", reply_markup=markup)
    
    photo_buttons_map[sent.message_id] = {
        'photo_id': m.message_id,
        'buttons_id': sent.message_id
    }


@bot.callback_query_handler(func=lambda c: True)
def photo_callback(c):
    data = photo_buttons_map.get(c.message.message_id)
    if not data:
        bot.answer_callback_query(c.id, "❌ Фото не найдено")
        return
    
    if c.data == 'meme':
        msg = bot.send_message(c.message.chat.id, "📝 Текст (верх | низ):")
        bot.register_next_step_handler(msg, create_meme_handler, c.message)
    
    elif c.data == 'compress':
        file = bot.get_file(data['photo_id'])
        downloaded = bot.download_file(file.file_path)
        compressed = compress_image(downloaded)
        bot.send_photo(c.message.chat.id, compressed, caption="🗜 Сжато")
    
    bot.answer_callback_query(c.id)


def create_meme_handler(m, original):
    data = photo_buttons_map.get(original.message_id)
    if not data:
        bot.send_message(m.chat.id, "❌ Фото не найдено")
        return
    
    parts = m.text.split('|')
    top = parts[0].strip() if parts else ''
    bottom = parts[1].strip() if len(parts) > 1 else ''
    
    file = bot.get_file(data['photo_id'])
    downloaded = bot.download_file(file.file_path)
    meme = create_meme(downloaded, top, bottom)
    
    bot.send_photo(m.chat.id, meme, caption="🎉 Мем готов!")


# ========== КУРСЫ ВАЛЮТ ==========

@bot.message_handler(func=lambda m: m.text == '💰 Курсы валют')
def currency_handler(m):
    wait = bot.send_message(m.chat.id, "⏳ Получаю курсы...")
    currency = get_currency()
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, currency, parse_mode='HTML')


# ========== ПОГОДА ==========

@bot.message_handler(func=lambda m: m.text == '🌤 Погода')
def weather_prompt(m):
    msg = bot.send_message(m.chat.id, "🌍 Город:")
    bot.register_next_step_handler(msg, weather_answer)


def weather_answer(m):
    wait = bot.send_message(m.chat.id, "⏳ Получаю погоду...")
    weather = get_weather(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, weather, parse_mode='HTML')


# ========== ПЕРЕВОД ==========

@bot.message_handler(func=lambda m: m.text == '🔤 Перевод')
def translate_prompt(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('🇬🇧 На английский', '🇷🇺 На русский', '🔙 Главное меню')
    msg = bot.send_message(m.chat.id, "🌐 Направление:", reply_markup=markup)
    bot.register_next_step_handler(msg, translate_lang)


def translate_lang(m):
    if m.text == '🔙 Главное меню':
        return start(m)
    
    user_data[m.chat.id] = 'en' if '🇬🇧' in m.text else 'ru'
    msg = bot.send_message(m.chat.id, "📝 Текст:")
    bot.register_next_step_handler(msg, translate_text_handler)


def translate_text_handler(m):
    wait = bot.send_message(m.chat.id, "⏳ Перевожу...")
    dest = user_data.get(m.chat.id, 'en')
    translated = translate(m.text, dest)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, f"🔤 {translated}")


# ========== ПОЗЫВНОЙ ==========

@bot.message_handler(func=lambda m: m.text == '🎯 Позывной')
def callsign_prompt(m):
    msg = bot.send_message(m.chat.id, "🎯 Слово:")
    bot.register_next_step_handler(msg, callsign_answer)


def callsign_answer(m):
    callsigns = get_callsign(m.text)
    text = "🎯 <b>Позывные:</b>\n\n" + "\n".join(callsigns)
    bot.send_message(m.chat.id, text, parse_mode='HTML')


# ========== ПОМОЩЬ ==========

@bot.message_handler(func=lambda m: m.text == '❓ Помощь')
def help_handler(m):
    text = "🤖 <b>DeepSeek</b> - любой вопрос\n"
    text += "🎨 <b>Картинка</b> - создание\n"
    text += "🎬 <b>Фильм</b> - по настроению\n"
    text += "📸 <b>Фото</b> - мемы, сжатие\n"
    text += "💰 <b>Курсы</b> - онлайн\n"
    text += "🌤 <b>Погода</b> - в любом городе\n"
    text += "🔤 <b>Перевод</b> - текста\n"
    text += "🎯 <b>Позывной</b> - генератор"
    bot.send_message(m.chat.id, text, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == '🔙 Главное меню')
def back_to_menu(m):
    start(m)


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("🤖 DeepSeek: активен")
    print("🎨 Генерация: активна")
    print("=" * 50)
    
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
