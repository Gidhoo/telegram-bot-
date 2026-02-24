import telebot as tb
from datetime import datetime
from telebot import types
import time
import threading
import requests
import random
import urllib.parse
import os

# ========== НАСТРОЙКИ ==========
TOKEN = "8529993544:AAEHluimYCHsEmZmMYVVBE7hZpKaR149v88"
YOUR_CHAT_ID = 1551325264

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)

# Словари для хранения данных
user_data = {}


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
    """Получает реальную погоду онлайн"""
    try:
        # Очищаем название города
        city = city.strip().lower()
        
        # Используем Open-Meteo API (бесплатно, без ключа)
        # Сначала получаем координаты города через геокодинг
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        
        if geo_response.status_code != 200:
            return f"❌ Город '{city}' не найден"
        
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return f"❌ Город '{city}' не найден"
        
        # Получаем координаты
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        city_name = geo_data['results'][0]['name']
        country = geo_data['results'][0].get('country', '')
        
        # Получаем погоду по координатам
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=auto"
        weather_response = requests.get(weather_url, timeout=5)
        
        if weather_response.status_code != 200:
            return f"❌ Не удалось получить погоду для города {city_name}"
        
        weather_data = weather_response.json()
        
        # Парсим данные
        current = weather_data['current_weather']
        temp = current['temperature']
        wind_speed = current['windspeed']
        
        # Получаем влажность из почасовых данных
        current_hour = datetime.now().hour
        humidity = weather_data['hourly']['relativehumidity_2m'][current_hour]
        
        # Определяем погодные условия
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
    
    # Вариант 1: Приставка + слово
    results.append(f"🎖 {random.choice(prefixes)} {word.title()}")
    
    # Вариант 2: слово + суффикс
    results.append(f"🎖 {word.title()} {random.choice(suffixes)}")
    
    # Вариант 3: Приставка + суффикс (без слова)
    results.append(f"🎖 {random.choice(prefixes)} {random.choice(suffixes)}")
    
    return results


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start', 'main', 'hello'])
def start_command(message):
    user_name = message.from_user.first_name

    # Главное меню - ТОЛЬКО РАБОЧИЕ КНОПКИ
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('💰 Курсы валют')
    btn2 = types.KeyboardButton('🎲 Факт')
    btn3 = types.KeyboardButton('😄 Анекдот')
    btn4 = types.KeyboardButton('🌤 Погода')
    btn5 = types.KeyboardButton('🔤 Перевод')
    btn6 = types.KeyboardButton('🕐 Время')
    btn7 = types.KeyboardButton('📅 Дата')
    btn8 = types.KeyboardButton('🎯 Позывной')
    btn9 = types.KeyboardButton('❓ Помощь')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)

    welcome_text = f"👋 Привет, {user_name}!\n\n"
    welcome_text += "Я бот. Выбери действие:\n\n"
    welcome_text += "💰 Курсы валют USD/EUR\n"
    welcome_text += "🎲 Случайные факты\n"
    welcome_text += "😄 Анекдоты\n"
    welcome_text += "🌤 Погода в любом городе\n"
    welcome_text += "🔤 Перевод текста\n"
    welcome_text += "🕐 Текущее время\n"
    welcome_text += "📅 Текущая дата\n"
    welcome_text += "🎯 Генератор позывных"

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# ========== ГЕНЕРАТОР ПОЗЫВНЫХ ==========

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
    help_text = "🔹 <b>Доступные команды:</b>\n\n"
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
        bot.send_message(message.chat.id, "🙏 Пожалуйста!")
    elif text == 'привет':
        bot.send_message(message.chat.id, f"👋 Привет, {message.from_user.first_name}!")
    elif text == 'id':
        bot.send_message(message.chat.id, f"🆔 Ваш ID: {message.from_user.id}")


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("📱 Версия: 5.0 (Только рабочие функции)")
    print("📱 Токен:", TOKEN[:10] + "...")
    print("=" * 50)
    print("📋 Доступные команды:")
    print("   • 💰 Курсы валют")
    print("   • 🎲 Факт")
    print("   • 😄 Анекдот")
    print("   • 🌤 Погода")
    print("   • 🔤 Перевод")
    print("   • 🎯 Позывной")
    print("   • 🕐 Время")
    print("   • 📅 Дата")
    print("=" * 50)

    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
