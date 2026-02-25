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
DEEPSEEK_KEY = "sk-d838f69da7794f3998464fd7ead477b9"

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)

# Словари для хранения данных
user_data = {}
photo_buttons_map = {}  # Для хранения фото


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
        
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        params = {
            "width": 1024,
            "height": 1024,
            "nologo": "true",
            "model": "flux"
        }
        
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
        "веселый": ["🎬 1+1 (2011) - Французская комедия", "🎬 Мальчишник в Вегасе (2009) - Комедия", "🎬 О чём говорят мужчины (2010) - Комедия"],
        "грустный": ["🎬 Побег из Шоушенка (1994) - Драма", "🎬 Зеленая миля (1999) - Драма", "🎬 Хатико (2009) - Драма"],
        "романтичный": ["🎬 500 дней лета (2009) - Романтика", "🎬 Гордость и предубеждение (2005) - Романтика", "🎬 Вечное сияние чистого разума (2004) - Фантастика, Романтика"],
        "страшный": ["🎬 Заклятие (2013) - Ужасы", "🎬 Астрал (2010) - Ужасы", "🎬 Оно (2017) - Ужасы"],
        "фантастика": ["🎬 Начало (2010) - Фантастика", "🎬 Интерстеллар (2014) - Фантастика", "🎬 Матрица (1999) - Фантастика"],
        "боевик": ["🎬 Тёмный рыцарь (2008) - Боевик", "🎬 Безумный Макс (2015) - Боевик", "🎬 Джон Уик (2014) - Боевик"],
        "детектив": ["🎬 Шерлок Холмс (2009) - Детектив", "🎬 Достать ножи (2019) - Детектив", "🎬 Семь (1995) - Детектив"]
    }
    
    mood = mood.lower()
    for key in recommendations:
        if key in mood:
            return random.choice(recommendations[key])
    
    all_movies = []
    for movies in recommendations.values():
        all_movies.extend(movies)
    return random.choice(all_movies)


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
    except Exception as e:
        print(f"Ошибка сжатия: {e}")
        return image_data


def create_meme_simple(image_data, top_text, bottom_text):
    """Простое создание мема"""
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
    except Exception as e:
        print(f"Ошибка создания мема: {e}")
        return image_data


# ========== КУРСЫ ВАЛЮТ (ОНЛАЙН) ==========

def get_currency_rates():
    """Получает актуальные курсы валют с сайта ЦБ РФ"""
    try:
        # Прямой запрос к сайту ЦБ РФ
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Получаем данные по всем основным валютам
            usd = data['Valute']['USD']['Value']
            eur = data['Valute']['EUR']['Value']
            cny = data['Valute']['CNY']['Value']  # Юань
            gbp = data['Valute']['GBP']['Value']  # Фунт
            jpy = data['Valute']['JPY']['Value']  # Йена
            
            # Получаем изменения за день
            usd_diff = data['Valute']['USD']['Previous'] - usd
            eur_diff = data['Valute']['EUR']['Previous'] - eur
            
            # Формируем красивое сообщение
            result = "💱 <b>Актуальные курсы валют:</b>\n\n"
            result += f"🇺🇸 USD: <b>{usd:.2f} ₽</b>"
            if usd_diff > 0:
                result += f" (📉 {usd_diff:.2f})\n"
            elif usd_diff < 0:
                result += f" (📈 {abs(usd_diff):.2f})\n"
            else:
                result += " (🔹 0.00)\n"
            
            result += f"🇪🇺 EUR: <b>{eur:.2f} ₽</b>"
            if eur_diff > 0:
                result += f" (📉 {eur_diff:.2f})\n"
            elif eur_diff < 0:
                result += f" (📈 {abs(eur_diff):.2f})\n"
            else:
                result += " (🔹 0.00)\n"
            
            result += f"🇨🇳 CNY: <b>{cny:.2f} ₽</b>\n"
            result += f"🇬🇧 GBP: <b>{gbp:.2f} ₽</b>\n"
            result += f"🇯🇵 JPY: <b>{jpy:.2f} ₽</b>\n\n"
            result += f"📅 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            result += f"📊 Данные: ЦБ РФ"
            
            return result
        else:
            return "❌ Не удалось получить курсы валют. Попробуйте позже."
            
    except Exception as e:
        print(f"Ошибка получения курсов: {e}")
        return get_currency_rates_fallback()


def get_currency_rates_fallback():
    """Запасной вариант получения курсов"""
    try:
        # Используем альтернативный источник
        response = requests.get("https://api.exchangerate-api.com/v4/latest/RUB", timeout=5)
        if response.status_code == 200:
            data = response.json()
            usd = 1 / data['rates']['USD']
            eur = 1 / data['rates']['EUR']
            return f"💱 Курсы валют:\n🇺🇸 USD: {usd:.2f} ₽\n🇪🇺 EUR: {eur:.2f} ₽\n\n📊 Данные: ExchangeRate-API"
    except:
        pass
    
    return "❌ Сервис временно недоступен"


# ========== ОСТАЛЬНЫЕ ФУНКЦИИ ==========

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
               f"💨 Ветер: <b>{wind_speed} км/ч</b>"
               
    except Exception as e:
        print(f"Ошибка погоды: {e}")
        return "❌ Ошибка при получении погоды"


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
        return "❌ Ошибка перевода"


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

    # Главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Кнопки нейросетей
    btn_ai1 = types.KeyboardButton('🤖 Спросить DeepSeek')
    btn_ai2 = types.KeyboardButton('🎨 Сгенерировать картинку')
    btn_ai3 = types.KeyboardButton('🎬 Фильм по настроению')
    
    # Кнопка для фото
    btn_photo = types.KeyboardButton('📸 Отправить фото')
    
    # Обычные кнопки
    btn_currency = types.KeyboardButton('💰 Курсы валют')
    btn_weather = types.KeyboardButton('🌤 Погода')
    btn_translate = types.KeyboardButton('🔤 Перевод')
    btn_callsign = types.KeyboardButton('🎯 Позывной')
    btn_help = types.KeyboardButton('❓ Помощь')
    
    # Добавляем кнопки в меню
    markup.add(btn_ai1, btn_ai2, btn_ai3)
    markup.add(btn_photo)
    markup.add(btn_currency, btn_weather, btn_translate, btn_callsign, btn_help)

    welcome_text = f"👋 Привет, {user_name}!\n\n"
    welcome_text += "🤖 <b>НЕЙРОСЕТИ:</b>\n"
    welcome_text += "• Спросить DeepSeek - задай любой вопрос\n"
    welcome_text += "• Сгенерировать картинку - опиши что хочешь\n"
    welcome_text += "• Фильм по настроению - подбор фильма\n\n"
    welcome_text += "📸 <b>ФОТО:</b>\n"
    welcome_text += "• Отправь фото - сделаем мем, сожмем или распознаем текст\n\n"
    welcome_text += "💰 <b>ДРУГИЕ ФУНКЦИИ:</b>\n"
    welcome_text += "• Курсы валют (онлайн)\n"
    welcome_text += "• Погода, перевод, позывной"

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')


# ========== НЕЙРОСЕТЕВЫЕ КОМАНДЫ ==========

@bot.message_handler(func=lambda message: message.text == '🤖 Спросить DeepSeek')
def ai_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🤖 <b>DeepSeek AI готов ответить!</b>\n\nЗадай любой вопрос:",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_ai_question)


def process_ai_question(message):
    try:
        question = message.text.strip()
        waiting = bot.send_message(message.chat.id, "⏳ DeepSeek думает...")
        
        response = get_deepseek_response(question)
        
        try:
            bot.delete_message(message.chat.id, waiting.message_id)
        except:
            pass
        
        bot.send_message(message.chat.id, f"🤖 <b>DeepSeek:</b>\n\n{response}", parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == '🎨 Сгенерировать картинку')
def image_prompt(message):
    msg = bot.send_message(message.chat.id, 
                          "🎨 <b>Генерация картинки</b>\n\nОпиши что хочешь увидеть:",
                          parse_mode='HTML')
    bot.register_next_step_handler(msg, process_image_generation)


def process_image_generation(message):
    try:
        prompt = message.text.strip()
        
        if len(prompt) < 3:
            bot.send_message(message.chat.id, "❌ Слишком короткое описание")
            return
        
        waiting = bot.send_message(message.chat.id, "🎨 Генерирую картинку... (до 30 секунд)")
        
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
            bot.send_message(message.chat.id, "❌ Не удалось сгенерировать картинку")
            
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
        
        bot.send_message(message.chat.id, f"🎬 <b>Рекомендация:</b>\n\n{movie}", parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")


# ========== ОБРАБОТКА ФОТО ==========

@bot.message_handler(func=lambda message: message.text == '📸 Отправить фото')
def photo_instruction(message):
    bot.send_message(message.chat.id, "📸 Отправьте мне фото (как изображение)")


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

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


@bot.callback_query_handler(func=lambda callback: True)
def callback_photo(callback):
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


# ========== ОБЫЧНЫЕ КОМАНДЫ ==========

@bot.message_handler(func=lambda message: message.text == '💰 Курсы валют')
def currency_command(message):
    msg = bot.send_message(message.chat.id, "⏳ Получаю актуальные курсы...")
    rates = get_currency_rates()
    try:
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        pass
    bot.send_message(message.chat.id, rates, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🌤 Погода')
def weather_prompt(message):
    msg = bot.send_message(message.chat.id, "🌍 Введите название города:")
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
    
    msg = bot.send_message(message.chat.id, f"📝 Введите текст для перевода на {target}:")
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
                          "🎯 <b>Генератор позывных</b>\n\nНапиши одно слово:",
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


@bot.message_handler(func=lambda message: message.text == '❓ Помощь')
def help_command(message):
    help_text = "🔹 <b>НЕЙРОСЕТИ:</b>\n"
    help_text += "🤖 Спросить DeepSeek - любой вопрос\n"
    help_text += "🎨 Сгенерировать картинку - создай изображение\n"
    help_text += "🎬 Фильм по настроению - подбор фильма\n\n"
    help_text += "🔹 <b>ФОТО:</b>\n"
    help_text += "📸 Отправить фото - мемы, сжатие, OCR\n\n"
    help_text += "🔹 <b>ДРУГИЕ:</b>\n"
    help_text += "💰 Курсы валют - актуальные онлайн\n"
    help_text += "🌤 Погода - в любом городе\n"
    help_text += "🔤 Перевод - текста\n"
    help_text += "🎯 Позывной - генератор"

    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(func=lambda message: message.text == '🔙 Главное меню')
def back_to_main(message):
    start_command(message)


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 60)
    print("✅ БОТ ЗАПУЩЕН!")
    print("📱 Версия: 8.0 (Финальная)")
    print("=" * 60)
    print("🤖 НЕЙРОСЕТИ:")
    print("   • Спросить DeepSeek")
    print("   • Генерация картинок")
    print("   • Фильмы по настроению")
    print("📸 ФОТО:")
    print("   • Мемы, сжатие, распознавание")
    print("💰 КУРСЫ ВАЛЮТ (онлайн):")
    print("   • USD, EUR, CNY, GBP, JPY")
    print("=" * 60)

    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
