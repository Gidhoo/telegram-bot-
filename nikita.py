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
from PIL import Image

# ========== НАСТРОЙКИ ==========
TOKEN = "8529993544:AAEHluimYCHsEmZmMYVVBE7hZpKaR149v88"
YOUR_CHAT_ID = 1551325264
DEEPSEEK_KEY = "sk-d838f69da7794f3998464fd7ead477b9"  # Ваш ключ DeepSeek

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)

# Словари для хранения данных
user_data = {}


# ========== НЕЙРОСЕТЕВЫЕ ФУНКЦИИ ==========

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
                {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко и понятно, но по делу."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"❌ Ошибка API: {response.status_code}"
            
    except Exception as e:
        return f"❌ Ошибка: {e}"


def generate_image(prompt):
    """Генерирует реальную картинку через Pollinations.ai"""
    try:
        print(f"🎨 Генерирую картинку: {prompt}")
        
        # Кодируем промпт для URL
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Формируем URL для генерации
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        # Добавляем параметры для лучшего качества
        params = {
            "width": 1024,
            "height": 1024,
            "nologo": "true",
            "model": "flux"
        }
        
        # Получаем картинку
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ Картинка сгенерирована!")
            return response.content
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return None


def get_movie_recommendation(mood):
    """Рекомендация фильма по настроению"""
    
    recommendations = {
        "веселый": ["🎬 1+1 (2011)", "🎬 Мальчишник в Вегасе (2009)", "🎬 О чём говорят мужчины (2010)"],
        "грустный": ["🎬 Побег из Шоушенка (1994)", "🎬 Зеленая миля (1999)", "🎬 Хатико (2009)"],
        "романтичный": ["🎬 500 дней лета (2009)", "🎬 Гордость и предубеждение (2005)", "🎬 Вечное сияние чистого разума (2004)"],
        "страшный": ["🎬 Заклятие (2013)", "🎬 Астрал (2010)", "🎬 Оно (2017)"],
        "фантастика": ["🎬 Начало (2010)", "🎬 Интерстеллар (2014)", "🎬 Матрица (1999)"],
        "боевик": ["🎬 Тёмный рыцарь (2008)", "🎬 Безумный Макс (2015)", "🎬 Джон Уик (2014)"],
        "детектив": ["🎬 Шерлок Холмс (2009)", "🎬 Достать ножи (2019)", "🎬 Семь (1995)"]
    }
    
    mood = mood.lower()
    for key in recommendations:
        if key in mood:
            return random.choice(recommendations[key])
    
    # Если настроение не определено
    all_movies = []
    for movies in recommendations.values():
        all_movies.extend(movies)
    return random.choice(all_movies)


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

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
        "🐧 Пингвины могут выпить морскую воду без вреда для здоровья",
    ]
    return random.choice(facts)


def get_joke():
    """Случайный анекдот"""
    jokes = [
        "— Дорогой, я решила стать вегетарианкой!\n— Зачем?\n— Чтобы спасти животных!\n— А ты знаешь, сколько растений погибает ради твоего спасения?",
        "Встречаются два программиста:\n— Ты знаешь, я вчера целый день искал себе девушку.\n— Ну и как, нашёл?\n— Нет, зато нашёл 404 ошибку.",
        "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что 31 Oct = 25 Dec",
        "Учительница спрашивает Вовочку:\n— Вовочка, почему ты опять опоздал?\n— Марья Ивановна, я спешил в школу, но увидел табличку «Школа — 50 метров» и решил, что успею пройти это расстояние за 50 секунд...",
        "— Доктор, у меня шизофрения!\n— А у меня аллергия на глупых пациентов.\n— А я люблю котиков!\n— Вот видите, мы уже нашли общий язык.",
    ]
    return random.choice(jokes)


def get_weather(city):
    """Получает реальную погоду онлайн"""
    try:
        city = city.strip().lower()
        
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
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=auto"
        weather_response = requests.get(weather_url, timeout=5)
        
        if weather_response.status_code != 200:
            return f"❌ Не удалось получить погоду для города {city_name}"
        
        weather_data = weather_response.json()
        
        current = weather_data['current_weather']
        temp = current['temperature']
        wind_speed = current['windspeed']
        
        current_hour = datetime.now().hour
        humidity = weather_data['hourly']['relativehumidity_2m'][current_hour]
        
        condition = get_condition(weather_data)
        
        return f"🌍 <b>{city_name}, {country}</b>\n\n" \
               f"🌡 Температура: <b>{temp:.1f}°C</b>\n" \
               f"☁️ {condition}\n" \
               f"💧 Влажность: <b>{humidity}%</b>\n" \
               f"💨 Ветер: <b>{wind_speed} км/ч</b>\n\n" \
               f"📡 Данные: Open-Meteo.com"
               
    except Exception as e:
        print(f"Ошибка погоды: {e}")
        return "❌ Ошибка при получении погоды. Попробуйте другой город."


def get_condition(weather_data):
    """Определяет погодные условия"""
    try:
        if 'current_weather' in weather_data and 'weathercode' in weather_data['current_weather']:
            code = weather_data['current_weather']['weathercode']
            conditions = {
                0: "☀️ Ясно",
                1: "🌤 Малооблачно",
                2: "⛅ Переменная облачность",
                3: "☁️ Пасмурно",
                45: "🌫 Туман",
                48: "🌫 Туман",
                51: "🌧 Морось",
                53: "🌧 Морось",
                55: "🌧 Морось",
                61: "🌧 Небольшой дождь",
                63: "🌧 Дождь",
                65: "🌧 Сильный дождь",
                71: "🌨 Небольшой снег",
                73: "🌨 Снег",
                75: "🌨 Сильный снег",
                80: "🌧 Дождь",
                81: "🌧 Дождь",
                82: "🌧 Сильный дождь",
                95: "⛈ Гроза",
                96: "⛈ Гроза",
                99: "⛈ Гроза"
            }
            return conditions.get(code, "☁️ Облачно")
    except:
        pass
    
    temp = weather_data['current_weather']['temperature']
    if temp > 25:
        return "☀️ Жарко"
    elif temp > 20:
        return "🌤 Тепло"
    elif temp > 10:
        return "⛅ Прохладно"
    elif temp > 0:
        return "☁️ Холодно"
    else:
        return "❄️ Морозно"


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
            
            if translated:
                return translated
            else:
                return "❌ Не удалось перевести текст"
        else:
            return "❌ Ошибка сервиса перевода"
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return "❌ Ошибка перевода. Попробуйте позже."


def generate_callsign(word):
    """Генерирует позывной на основе одного слова"""
    
    prefixes = ["Тихий", "Быстрый", "Дикий", "Мудрый", "Хитрый", 
                "Смелый", "Вольный", "Ярый", "Северный", "Стальной",
                "Огненный", "Ледяной", "Грозовой", "Солнечный", "Лунный"]
    
    suffixes = ["Волк", "Лис", "Медведь", "Орёл", "Сокол", 
                "Барс", "Рысь", "Тигр", "Лев", "Ворон",
                "Шторм", "Ветер", "Гром", "Молния", "Коготь"]
    
    word = word.strip().lower()
    results = []
    
    results.append(f"🎖 {random.choice(prefixes)} {word.title()}")
    results.append(f"🎖 {word.title()} {random.choice(suffixes)}")
    results.append(f"🎖 {random.choice(prefixes)} {random.choice(suffixes)}")
    
    return results


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start', 'main', 'hello'])
def start_command(message):
    user_name = message.from_user.first_name

    # Главное меню с нейросетями
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Кнопки нейросетей
    btn_ai1 = types.KeyboardButton('🤖 Спросить DeepSeek')
    btn_ai2 = types.KeyboardButton('🎨 Сгенерировать картинку')
    btn_ai3 = types.KeyboardButton('🎬 Фильм по настроению')
    
    # Обычные кнопки
    btn1 = types.KeyboardButton('💰 Курсы валют')
    btn2 = types.KeyboardButton('🎲 Факт')
    btn3 = types.KeyboardButton('😄 Анекдот')
    btn4 = types.KeyboardButton('🌤 Погода')
    btn5 = types.KeyboardButton('🔤 Перевод')
    btn6 = types.KeyboardButton('🕐 Время')
    btn7 = types.KeyboardButton('📅 Дата')
    btn8 = types.KeyboardButton('🎯 Позывной')
    btn9 = types.KeyboardButton('❓ Помощь')
    
    # Добавляем кнопки в меню
    markup.add(btn_ai1, btn_ai2, btn_ai3)
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)

    welcome_text = f"👋 Привет, {user_name}!\n\n"
    welcome_text += "🤖 <b>НЕЙРОСЕТИ (DeepSeek):</b>\n"
    welcome_text += "• Спросить DeepSeek - задай любой вопрос (как мне)\n"
    welcome_text += "• Сгенерировать картинку - опиши что хочешь\n"
    welcome_text += "• Фильм по настроению - нейросеть подберет фильм\n\n"
    welcome_text += "📱 <b>Обычные функции:</b>\n"
    welcome_text += "💰 Курсы валют, 🎲 Факты, 😄 Анекдоты\n"
    welcome_text += "🌤 Погода, 🔤 Перевод, 🕐 Время, 📅 Дата\n"
    welcome_text += "🎯 Позывной\n\n"
    welcome_text += "Выбери действие!"

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')


# ========== НЕЙРОСЕТЕВЫЕ КОМАНДЫ ==========

@bot.message_handler(func=lambda message: message.text == '🤖 Спросить DeepSeek')
def ai_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🤖 <b>DeepSeek AI готов ответить!</b>\n\n"
                          "Задай любой вопрос (можешь спросить как у меня):",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_ai_question)


def process_ai_question(message):
    try:
        question = message.text.strip()
        waiting = bot.send_message(message.chat.id, "⏳ DeepSeek думает...")
        
        # Получаем ответ от DeepSeek
        response = get_deepseek_response(question)
        
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except:
            pass
        
        # Отправляем ответ (если слишком длинный, разбиваем)
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                bot.send_message(message.chat.id, f"🤖 <b>DeepSeek:</b>\n\n{part}", parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, f"🤖 <b>DeepSeek:</b>\n\n{response}", parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == '🎨 Сгенерировать картинку')
def image_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎨 <b>Генерация картинки</b>\n\n"
                          "Опиши что хочешь увидеть (на русском или английском):\n"
                          "Например: 'красивый закат в горах', 'робот играет на пианино', 'киберпанк город'",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_image_generation)


def process_image_generation(message):
    try:
        prompt = message.text.strip()
        
        if len(prompt) < 3:
            bot.send_message(message.chat.id, "❌ Слишком короткое описание")
            return
        
        waiting = bot.send_message(message.chat.id, "🎨 Генерирую картинку... (до 30 секунд)")
        
        # Генерируем картинку
        image_data = generate_image(prompt)
        
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except:
            pass
        
        if image_data:
            bot.send_photo(
                message.chat.id, 
                image_data, 
                caption=f"🎨 <b>Ваша картинка:</b> {prompt}",
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                message.chat.id, 
                "❌ Не удалось сгенерировать картинку. Попробуйте другое описание."
            )
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == '🎬 Фильм по настроению')
def movie_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎬 <b>Какое у тебя настроение?</b>\n\n"
                          "Напиши: веселый, грустный, романтичный, страшный, фантастика, боевик, детектив",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_movie)


def process_movie(message):
    try:
        mood = message.text.strip()
        waiting = bot.send_message(message.chat.id, "⏳ Нейросеть подбирает фильм...")
        
        movie = get_movie_recommendation(mood)
        
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except:
            pass
        
        bot.send_message(message.chat.id, f"🎬 <b>Рекомендация для настроения '{mood}':</b>\n\n{movie}", parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


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
                          "🌍 Введите название города:",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_weather)


def process_weather(message):
    city = message.text.strip()
    waiting = bot.send_message(message.chat.id, "⏳ Получаю данные...")
    weather = get_weather(city)
    
    try:
        bot.delete_message(message.chat.id, waiting.message_id)
    except:
        pass
    
    bot.send_message(message.chat.id, weather, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔤 Перевод')
def translate_prompt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('🇬🇧 На английский')
    btn2 = types.KeyboardButton('🇷🇺 На русский')
    btn3 = types.KeyboardButton('🔙 Главное меню')
    markup.add(btn1, btn2, btn3)
    
    msg = bot.send_message(message.chat.id, 
                          "🌐 Выберите направление перевода:",
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
                          f"📝 Введите текст для перевода на {target}:")
    bot.register_next_step_handler(msg, process_translate_text)


def process_translate_text(message):
    try:
        dest = user_data.get(message.chat.id, 'en')
        waiting = bot.send_message(message.chat.id, "⏳ Перевожу...")
        translated = translate_text(message.text, dest)
        
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except:
            pass
        
        bot.send_message(message.chat.id, f"🔤 <b>Перевод:</b>\n\n{translated}", parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")


@bot.message_handler(func=lambda message: message.text == '🎯 Позывной')
def callsign_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎯 <b>Генератор позывных</b>\n\n"
                          "Напиши одно слово (например: волк, космос, гроза):",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_callsign)


def process_callsign(message):
    try:
        word = message.text.strip()
        
        if not word or len(word) > 20:
            bot.send_message(message.chat.id, "❌ Напиши одно слово (до 20 символов)")
            return
        
        results = generate_callsign(word)
        
        response = f"🎯 <b>Позывные для слова '{word.title()}':</b>\n\n"
        for result in results:
            response += f"{result}\n"
        
        bot.send_message(message.chat.id, response, parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


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
    help_text = "🔹 <b>НЕЙРОСЕТИ (DeepSeek):</b>\n"
    help_text += "🤖 Спросить DeepSeek - задай любой вопрос\n"
    help_text += "🎨 Сгенерировать картинку - создай изображение\n"
    help_text += "🎬 Фильм по настроению - подбор фильма\n\n"
    help_text += "🔹 <b>Обычные функции:</b>\n"
    help_text += "💰 Курсы валют - USD и EUR\n"
    help_text += "🎲 Факт - интересный факт\n"
    help_text += "😄 Анекдот - поднять настроение\n"
    help_text += "🌤 Погода - погода в любом городе\n"
    help_text += "🔤 Перевод - перевод текста\n"
    help_text += "🎯 Позывной - генератор позывных\n"
    help_text += "🕐 Время - текущее время\n"
    help_text += "📅 Дата - текущая дата"

    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔙 Главное меню')
def back_to_main(message):
    start_command(message)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.lower()
    
    if text in ['спасибо', 'спс', 'благодарю']:
        bot.send_message(message.chat.id, "🙏 Пожалуйста! Обращайся!")
    elif text == 'привет':
        bot.send_message(message.chat.id, f"👋 Привет, {message.from_user.first_name}!")
    elif text == 'id':
        bot.send_message(message.chat.id, f"🆔 Ваш ID: {message.from_user.id}")
    elif text == 'пока':
        bot.send_message(message.chat.id, "👋 До встречи!")


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 60)
    print("✅ БОТ С DEEPSEEK AI ЗАПУЩЕН!")
    print("📱 Версия: 7.0 (DeepSeek + генерация картинок)")
    print("📱 Токен:", TOKEN[:10] + "...")
    print("🔑 DeepSeek ключ:", DEEPSEEK_KEY[:10] + "...")
    print("=" * 60)
    print("🤖 НЕЙРОСЕТЕВЫЕ ФУНКЦИИ:")
    print("   • Спросить DeepSeek (как я)")
    print("   • Генерация картинок")
    print("   • Фильмы по настроению")
    print("=" * 60)
    print("📋 Обычные функции:")
    print("   • 💰 Курсы валют, 🎲 Факт, 😄 Анекдот")
    print("   • 🌤 Погода, 🔤 Перевод, 🎯 Позывной")
    print("   • 🕐 Время, 📅 Дата")
    print("=" * 60)

    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
