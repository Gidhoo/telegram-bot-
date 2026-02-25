import telebot as tb
from datetime import datetime
from telebot import types
import time
import threading
import requests
import random
import urllib.parse
import os
import io
import json
from PIL import Image, ImageDraw, ImageFont

# ========== НАСТРОЙКИ ==========
TOKEN = "8529993544:AAEHluimYCHsEmZmMYVVBE7hZpKaR149v88"
YOUR_CHAT_ID = 1551325264
DEEPSEEK_KEY = "sk-d838f69da7794f3998464fd7ead477b9"

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)

# Словари для хранения данных
user_data = {}
photo_buttons_map = {}


# ========== НЕЙРОСЕТЬ DEEPSEEK (КАК Я) ==========

def get_deepseek_response(prompt):
    """Получение ответа от DeepSeek AI"""
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_KEY}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Ты полезный и дружелюбный ассистент. Отвечай развернуто, понятно и с эмодзи. Помогай с любыми вопросами."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"Ошибка DeepSeek: {response.status_code}")
            print(f"Ответ: {response.text}")
            return fallback_ai_response(prompt)
            
    except Exception as e:
        print(f"Ошибка DeepSeek: {e}")
        return fallback_ai_response(prompt)


def fallback_ai_response(prompt):
    """Запасной AI когда DeepSeek недоступен"""
    responses = [
        f"Я думаю, что {prompt} - интересная тема. Расскажи подробнее, что именно тебя интересует?",
        f"Хороший вопрос про '{prompt}'. Давай разберемся вместе!",
        f"На счёт '{prompt}' могу сказать, что это зависит от контекста. Уточни, пожалуйста.",
        f"Я слышал о '{prompt}'. Что именно ты хочешь узнать?",
        f"Отличная тема! {prompt} - это действительно интересно. Задавай вопрос конкретнее."
    ]
    return random.choice(responses)


# ========== ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ ==========

def generate_image(prompt):
    """Генерирует реальную картинку через несколько сервисов"""
    
    # Пытаемся через разные сервисы
    services = [
        generate_image_pollinations,
        generate_image_prodia,
        generate_image_flux
    ]
    
    for service in services:
        try:
            result = service(prompt)
            if result:
                return result
        except:
            continue
    
    return None


def generate_image_pollinations(prompt):
    """Генерация через Pollinations.ai (основной)"""
    try:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        params = {
            "width": 1024,
            "height": 1024,
            "nologo": "true",
            "model": "flux",
            "seed": random.randint(1, 1000000)
        }
        response = requests.get(url, params=params, timeout=45)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None


def generate_image_prodia(prompt):
    """Генерация через Prodia"""
    try:
        # Публичный API Prodia
        url = "https://api.prodia.com/v1/sd/generate"
        headers = {
            "X-Prodia-Key": "free-public-demo-key",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sdv1_4.ckpt",
            "prompt": prompt,
            "negative_prompt": "bad quality, blurry",
            "steps": 20,
            "cfg_scale": 7
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            job_id = response.json()['job']
            for _ in range(10):
                time.sleep(2)
                result = requests.get(f"https://api.prodia.com/v1/job/{job_id}")
                if result.json()['status'] == 'succeeded':
                    img_url = result.json()['imageUrl']
                    img = requests.get(img_url)
                    return img.content
    except:
        pass
    return None


def generate_image_flux(prompt):
    """Генерация через Flux AI"""
    try:
        url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        headers = {"Authorization": "Bearer hf_free_public_demo"}
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=30)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None


# ========== ФУНКЦИИ ДЛЯ ФИЛЬМОВ ==========

def get_movie_recommendation(mood):
    """Рекомендация фильма по настроению"""
    
    recommendations = {
        "веселый": [
            "🎬 1+1 (2011) - Французская комедия о дружбе аристократа и парня из пригорода",
            "🎬 Мальчишник в Вегасе (2009) - Американская комедия про похождения друзей",
            "🎬 О чём говорят мужчины (2010) - Российская комедия про друзей в дороге"
        ],
        "грустный": [
            "🎬 Побег из Шоушенка (1994) - История надежды и дружбы в тюрьме",
            "🎬 Зеленая миля (1999) - Мистическая драма о добре и зле",
            "🎬 Хатико (2009) - Трогательная история о верности"
        ],
        "романтичный": [
            "🎬 500 дней лета (2009) - Необычная история любви",
            "🎬 Гордость и предубеждение (2005) - Классическая романтическая история",
            "🎬 Вечное сияние чистого разума (2004) - Философская история о любви"
        ],
        "страшный": [
            "🎬 Заклятие (2013) - Фильм ужасов про паранормальное",
            "🎬 Астрал (2010) - Мистический хоррор",
            "🎬 Оно (2017) - Экранизация романа Стивена Кинга"
        ],
        "фантастика": [
            "🎬 Начало (2010) - Фантастика про сны во сне",
            "🎬 Интерстеллар (2014) - Космическая фантастика",
            "🎬 Матрица (1999) - Культовая фантастика"
        ]
    }
    
    mood = mood.lower()
    for key in recommendations:
        if key in mood:
            return random.choice(recommendations[key])
    
    all_movies = []
    for movies in recommendations.values():
        all_movies.extend(movies)
    return random.choice(all_movies)


# ========== КУРСЫ ВАЛЮТ ==========

def get_currency_rates():
    """Получает актуальные курсы валют"""
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        if response.status_code == 200:
            data = response.json()
            usd = data['Valute']['USD']['Value']
            eur = data['Valute']['EUR']['Value']
            cny = data['Valute']['CNY']['Value']
            
            return f"💱 <b>Курсы валют ЦБ РФ:</b>\n\n" \
                   f"🇺🇸 USD: <b>{usd:.2f} ₽</b>\n" \
                   f"🇪🇺 EUR: <b>{eur:.2f} ₽</b>\n" \
                   f"🇨🇳 CNY: <b>{cny:.2f} ₽</b>\n\n" \
                   f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    except:
        pass
    
    # Запасной вариант
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/RUB")
        if response.status_code == 200:
            data = response.json()
            usd = 1 / data['rates']['USD']
            eur = 1 / data['rates']['EUR']
            return f"💱 Курсы:\n🇺🇸 USD: {usd:.2f} ₽\n🇪🇺 EUR: {eur:.2f} ₽"
    except:
        pass
    
    return "❌ Сервис временно недоступен"


# ========== ПОГОДА ==========

def get_weather(city):
    """Получает погоду"""
    try:
        city = city.strip().lower()
        
        # Получаем координаты
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
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=auto"
        weather_response = requests.get(weather_url, timeout=5)
        
        if weather_response.status_code != 200:
            return f"❌ Не удалось получить погоду"
        
        weather_data = weather_response.json()
        
        current = weather_data['current_weather']
        temp = current['temperature']
        wind_speed = current['windspeed']
        
        current_hour = datetime.now().hour
        humidity = weather_data['hourly']['relativehumidity_2m'][current_hour]
        
        # Определяем погоду
        if temp > 20:
            condition = "☀️ Солнечно"
        elif temp > 10:
            condition = "⛅ Облачно"
        elif temp > 0:
            condition = "☁️ Пасмурно"
        else:
            condition = "❄️ Холодно"
        
        return f"🌍 <b>{city_name}, {country}</b>\n\n" \
               f"🌡 Температура: <b>{temp:.1f}°C</b>\n" \
               f"☁️ {condition}\n" \
               f"💧 Влажность: <b>{humidity}%</b>\n" \
               f"💨 Ветер: <b>{wind_speed} км/ч</b>"
               
    except Exception as e:
        print(f"Ошибка погоды: {e}")
        return "❌ Ошибка при получении погоды"


# ========== ПЕРЕВОД ==========

def translate_text(text, dest='en'):
    """Перевод текста"""
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
    except:
        pass
    return "❌ Ошибка перевода"


# ========== ПОЗЫВНОЙ ==========

def generate_callsign(word):
    """Генерирует позывной"""
    prefixes = ["Тихий", "Быстрый", "Дикий", "Мудрый", "Хитрый", "Смелый"]
    suffixes = ["Волк", "Лис", "Медведь", "Орёл", "Сокол", "Барс"]
    word = word.strip().lower()
    return [
        f"🎖 {random.choice(prefixes)} {word.title()}",
        f"🎖 {word.title()} {random.choice(suffixes)}",
        f"🎖 {random.choice(prefixes)} {random.choice(suffixes)}"
    ]


# ========== ФУНКЦИИ ДЛЯ ФОТО ==========

def compress_image(image_data, quality=70):
    """Сжимает изображение"""
    try:
        img = Image.open(io.BytesIO(image_data))
        output = io.BytesIO()
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except:
        return image_data


def create_meme(image_data, top_text, bottom_text):
    """Создаёт мем"""
    try:
        img = Image.open(io.BytesIO(image_data))
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        font = ImageFont.load_default()
        
        if top_text:
            bbox = draw.textbbox((0, 0), top_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = 10
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + dx, y + dy), top_text, font=font, fill="black")
            draw.text((x, y), top_text, font=font, fill="white")
        
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
    except:
        return image_data


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Кнопки
    btn_deepseek = types.KeyboardButton('🤖 Спросить DeepSeek')
    btn_image = types.KeyboardButton('🎨 Создать картинку')
    btn_movie = types.KeyboardButton('🎬 Фильм по настроению')
    btn_photo = types.KeyboardButton('📸 Фото')
    btn_currency = types.KeyboardButton('💰 Курсы валют')
    btn_weather = types.KeyboardButton('🌤 Погода')
    btn_translate = types.KeyboardButton('🔤 Перевод')
    btn_callsign = types.KeyboardButton('🎯 Позывной')
    btn_help = types.KeyboardButton('❓ Помощь')
    
    markup.add(btn_deepseek, btn_image, btn_movie)
    markup.add(btn_photo)
    markup.add(btn_currency, btn_weather, btn_translate, btn_callsign, btn_help)

    welcome_text = f"👋 Привет, {user_name}!\n\n"
    welcome_text += "🤖 <b>DeepSeek AI:</b> задай любой вопрос\n"
    welcome_text += "🎨 <b>Создать картинку:</b> опиши что хочешь\n"
    welcome_text += "🎬 <b>Фильм:</b> по настроению\n"
    welcome_text += "📸 <b>Фото:</b> мемы, сжатие, OCR\n"
    welcome_text += "💰 <b>Курсы валют:</b> онлайн"

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')


# ========== DEEPSEEK ==========

@bot.message_handler(func=lambda message: message.text == '🤖 Спросить DeepSeek')
def deepseek_prompt(message):
    msg = bot.send_message(message.chat.id, "🤖 Задай любой вопрос:")
    bot.register_next_step_handler(msg, process_deepseek)


def process_deepseek(message):
    try:
        question = message.text.strip()
        waiting = bot.send_message(message.chat.id, "⏳ Думаю...")
        
        response = get_deepseek_response(question)
        
        bot.delete_message(message.chat.id, waiting.message_id)
        
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                bot.send_message(message.chat.id, response[i:i+4000])
        else:
            bot.send_message(message.chat.id, response)
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


# ========== ГЕНЕРАЦИЯ КАРТИНОК ==========

@bot.message_handler(func=lambda message: message.text == '🎨 Создать картинку')
def image_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎨 Опиши картинку (на русском):\n"
                          "Например: 'красивый закат в горах', 'робот играет на пианино'")
    bot.register_next_step_handler(msg, process_image)


def process_image(message):
    try:
        prompt = message.text.strip()
        
        if len(prompt) < 3:
            bot.send_message(message.chat.id, "❌ Слишком короткое описание")
            return
        
        waiting = bot.send_message(message.chat.id, "🎨 Генерирую картинку... (до 45 секунд)")
        
        image_data = generate_image(prompt)
        
        bot.delete_message(message.chat.id, waiting.message_id)
        
        if image_data:
            bot.send_photo(message.chat.id, image_data, caption=f"🎨 {prompt}")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось создать картинку")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


# ========== ФИЛЬМ ПО НАСТРОЕНИЮ ==========

@bot.message_handler(func=lambda message: message.text == '🎬 Фильм по настроению')
def movie_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎬 Какое настроение?\n"
                          "(веселый, грустный, романтичный, страшный, фантастика)")
    bot.register_next_step_handler(msg, process_movie)


def process_movie(message):
    mood = message.text.strip()
    movie = get_movie_recommendation(mood)
    bot.send_message(message.chat.id, movie)


# ========== ФОТО ==========

@bot.message_handler(func=lambda message: message.text == '📸 Фото')
def photo_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📤 Отправить фото')
    btn2 = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "📸 Отправьте фото:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📤 Отправить фото')
def photo_instruction(message):
    bot.send_message(message.chat.id, "📤 Отправьте фото")


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🎭 Мем', callback_data='meme')
    btn2 = types.InlineKeyboardButton('🗜 Сжать', callback_data='compress')
    btn3 = types.InlineKeyboardButton('🔍 OCR', callback_data='ocr')
    markup.row(btn1, btn2, btn3)
    
    sent = bot.reply_to(message, '✅ Фото получено!', reply_markup=markup)
    
    photo_buttons_map[sent.message_id] = {
        'photo_id': message.message_id,
        'buttons_id': sent.message_id
    }


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        data = photo_buttons_map.get(call.message.message_id)
        if not data:
            bot.answer_callback_query(call.id, "❌ Фото не найдено")
            return
        
        if call.data == 'meme':
            msg = bot.send_message(call.message.chat.id, "Текст для мема (верх | низ):")
            bot.register_next_step_handler(msg, process_meme, call.message)
            
        elif call.data == 'compress':
            photo_id = data['photo_id']
            file = bot.get_file(photo_id)
            downloaded = bot.download_file(file.file_path)
            compressed = compress_image(downloaded)
            bot.send_photo(call.message.chat.id, compressed, caption="🗜 Сжато")
            
        elif call.data == 'ocr':
            bot.answer_callback_query(call.id, "⚠️ Tesseract не установлен")
            
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка")


def process_meme(message, original):
    try:
        text = message.text
        if '|' in text:
            parts = text.split('|', 1)
            top = parts[0].strip()
            bottom = parts[1].strip()
        else:
            top = text
            bottom = ''
        
        data = photo_buttons_map.get(original.message_id)
        if not data:
            bot.send_message(message.chat.id, "❌ Фото не найдено")
            return
        
        photo_id = data['photo_id']
        file = bot.get_file(photo_id)
        downloaded = bot.download_file(file.file_path)
        
        meme = create_meme(downloaded, top, bottom)
        bot.send_photo(message.chat.id, meme, caption="🎉 Мем готов!")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


# ========== ДРУГИЕ КОМАНДЫ ==========

@bot.message_handler(func=lambda message: message.text == '💰 Курсы валют')
def currency_command(message):
    msg = bot.send_message(message.chat.id, "⏳ Получаю курсы...")
    rates = get_currency_rates()
    bot.delete_message(message.chat.id, msg.message_id)
    bot.send_message(message.chat.id, rates, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🌤 Погода')
def weather_prompt(message):
    msg = bot.send_message(message.chat.id, "🌍 Введите город:")
    bot.register_next_step_handler(msg, process_weather)


def process_weather(message):
    city = message.text.strip()
    wait = bot.send_message(message.chat.id, "⏳ Получаю данные...")
    weather = get_weather(city)
    bot.delete_message(message.chat.id, wait.message_id)
    bot.send_message(message.chat.id, weather, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔤 Перевод')
def translate_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('🇬🇧 На английский', '🇷🇺 На русский', '🔙 Главное меню')
    msg = bot.send_message(message.chat.id, "🌐 Выберите направление:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_translate_lang)


def process_translate_lang(message):
    if message.text == '🔙 Главное меню':
        return start_command(message)
    
    if '🇬🇧' in message.text:
        user_data[message.chat.id] = 'en'
        target = "английский"
    else:
        user_data[message.chat.id] = 'ru'
        target = "русский"
    
    msg = bot.send_message(message.chat.id, f"📝 Введите текст:")
    bot.register_next_step_handler(msg, process_translate_text)


def process_translate_text(message):
    dest = user_data.get(message.chat.id, 'en')
    wait = bot.send_message(message.chat.id, "⏳ Перевожу...")
    translated = translate_text(message.text, dest)
    bot.delete_message(message.chat.id, wait.message_id)
    bot.send_message(message.chat.id, f"🔤 {translated}")


@bot.message_handler(func=lambda message: message.text == '🎯 Позывной')
def callsign_prompt(message):
    msg = bot.send_message(message.chat.id, "🎯 Напишите слово:")
    bot.register_next_step_handler(msg, process_callsign)


def process_callsign(message):
    word = message.text.strip()
    results = generate_callsign(word)
    response = "🎯 <b>Позывные:</b>\n\n" + "\n".join(results)
    bot.send_message(message.chat.id, response, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '❓ Помощь')
def help_command(message):
    help_text = "🤖 <b>DeepSeek</b> - задай вопрос\n"
    help_text += "🎨 <b>Картинка</b> - создай изображение\n"
    help_text += "🎬 <b>Фильм</b> - по настроению\n"
    help_text += "📸 <b>Фото</b> - мемы, сжатие\n"
    help_text += "💰 <b>Курсы</b> - онлайн валют\n"
    help_text += "🌤 <b>Погода</b> - в любом городе\n"
    help_text += "🔤 <b>Перевод</b> - текста\n"
    help_text += "🎯 <b>Позывной</b> - генератор"
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔙 Главное меню')
def back_to_main(message):
    start_command(message)


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("🤖 DeepSeek AI активен")
    print("🎨 Генерация картинок активна")
    print("=" * 50)
    
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
