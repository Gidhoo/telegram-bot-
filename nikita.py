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


# ========== DEEPSEEK AI (ИСПРАВЛЕНО) ==========

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
                {
                    "role": "system", 
                    "content": "Ты умный AI-ассистент. Отвечай на вопросы максимально подробно и полезно. Используй эмодзи."
                },
                {"role": "user", "content": question}
            ],
            "temperature": 1.0,
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


# ========== ГЕНЕРАЦИЯ КАРТИНОК (РАБОЧАЯ) ==========

def generate_image_simple(prompt):
    """ПРОСТАЯ и РАБОЧАЯ генерация картинок"""
    try:
        # Используем самый надежный бесплатный API
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
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
            print(f"Ошибка генерации: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# ========== КУРСЫ ВАЛЮТ ==========

def get_currency():
    """Курсы валют онлайн"""
    try:
        r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        if r.status_code == 200:
            data = r.json()
            usd = data['Valute']['USD']['Value']
            eur = data['Valute']['EUR']['Value']
            cny = data['Valute']['CNY']['Value']
            
            text = f"💰 <b>Курсы ЦБ РФ</b>\n\n"
            text += f"🇺🇸 USD: <b>{usd:.2f} ₽</b>\n"
            text += f"🇪🇺 EUR: <b>{eur:.2f} ₽</b>\n"
            text += f"🇨🇳 CNY: <b>{cny:.2f} ₽</b>\n"
            text += f"\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            return text
    except:
        pass
    return "❌ Курсы временно недоступны"


# ========== ПОГОДА ==========

def get_weather(city):
    """Погода в городе"""
    try:
        # Получаем координаты
        geo = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_r = requests.get(geo, timeout=5)
        
        if geo_r.status_code != 200:
            return f"❌ Город '{city}' не найден"
        
        geo_data = geo_r.json()
        if not geo_data.get('results'):
            return f"❌ Город '{city}' не найден"
        
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        name = geo_data['results'][0]['name']
        country = geo_data['results'][0].get('country', '')
        
        # Получаем погоду
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_r = requests.get(w_url, timeout=5)
        
        if w_r.status_code != 200:
            return f"❌ Не удалось получить погоду"
        
        w_data = w_r.json()['current_weather']
        temp = w_data['temperature']
        wind = w_data['windspeed']
        
        # Погодные условия
        if temp > 20:
            cond = "☀️ Солнечно"
        elif temp > 10:
            cond = "⛅ Облачно"
        elif temp > 0:
            cond = "☁️ Пасмурно"
        else:
            cond = "❄️ Холодно"
        
        return f"🌍 <b>{name}, {country}</b>\n\n🌡 {temp}°C {cond}\n💨 Ветер: {wind} км/ч"
        
    except Exception as e:
        return f"❌ Ошибка: {e}"


# ========== ПЕРЕВОД ==========

def translate(text, dest='en'):
    """Перевод текста"""
    try:
        enc = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={dest}&dt=t&q={enc}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            res = r.json()
            trans = ''
            for s in res[0]:
                if s and s[0]:
                    trans += s[0]
            return trans
    except:
        pass
    return "❌ Ошибка перевода"


# ========== ФИЛЬМЫ ==========

def get_movie(mood):
    """Рекомендация фильма"""
    movies = {
        "веселый": "🎬 1+1 (2011) - Комедия",
        "грустный": "🎬 Побег из Шоушенка (1994) - Драма",
        "романтичный": "🎬 500 дней лета (2009) - Романтика",
        "страшный": "🎬 Заклятие (2013) - Ужасы",
        "фантастика": "🎬 Начало (2010) - Фантастика",
    }
    for k in movies:
        if k in mood.lower():
            return movies[k]
    return "🎬 1+1 (2011)"


# ========== ПОЗЫВНОЙ ==========

def callsign(word):
    """Генератор позывных"""
    pre = ["Тихий", "Быстрый", "Дикий", "Мудрый", "Смелый"]
    suf = ["Волк", "Лис", "Медведь", "Орёл", "Сокол"]
    w = word.strip().title()
    return [
        f"🎖 {random.choice(pre)} {w}",
        f"🎖 {w} {random.choice(suf)}",
        f"🎖 {random.choice(pre)} {random.choice(suf)}"
    ]


# ========== ФУНКЦИИ ДЛЯ ФОТО ==========

def make_meme(img_data, top, bottom):
    """Создание мема"""
    try:
        img = Image.open(io.BytesIO(img_data))
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        font = ImageFont.load_default()
        
        if top:
            bbox = draw.textbbox((0, 0), top, font=font)
            x = (w - (bbox[2] - bbox[0])) // 2
            y = 10
            draw.text((x, y), top, font=font, fill="white")
        
        if bottom:
            bbox = draw.textbbox((0, 0), bottom, font=font)
            x = (w - (bbox[2] - bbox[0])) // 2
            y = h - (bbox[3] - bbox[1]) - 10
            draw.text((x, y), bottom, font=font, fill="white")
        
        out = io.BytesIO()
        img.save(out, format='JPEG')
        return out.getvalue()
    except:
        return img_data


def compress(img_data):
    """Сжатие фото"""
    try:
        img = Image.open(io.BytesIO(img_data))
        out = io.BytesIO()
        img.save(out, format='JPEG', quality=70, optimize=True)
        return out.getvalue()
    except:
        return img_data


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    markup.add(
        types.KeyboardButton('🤖 DeepSeek'),
        types.KeyboardButton('🎨 Картинка'),
        types.KeyboardButton('🎬 Фильм'),
        types.KeyboardButton('📸 Фото'),
        types.KeyboardButton('💰 Курсы'),
        types.KeyboardButton('🌤 Погода'),
        types.KeyboardButton('🔤 Перевод'),
        types.KeyboardButton('🎯 Позывной'),
        types.KeyboardButton('❓ Помощь')
    )
    
    text = f"👋 Привет, {m.from_user.first_name}!\n\n"
    text += "🤖 DeepSeek - любой вопрос\n"
    text += "🎨 Картинка - создай изображение\n"
    text += "🎬 Фильм - по настроению\n"
    text += "📸 Фото - мемы и сжатие"
    
    bot.send_message(m.chat.id, text, reply_markup=markup)


# ========== DEEPSEEK ==========

@bot.message_handler(func=lambda m: m.text == '🤖 DeepSeek')
def deepseek_prompt(m):
    msg = bot.send_message(m.chat.id, "🤖 Вопрос:")
    bot.register_next_step_handler(msg, deepseek_answer)


def deepseek_answer(m):
    wait = bot.send_message(m.chat.id, "⏳ Думаю...")
    ans = ask_deepseek(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, ans)


# ========== КАРТИНКИ ==========

@bot.message_handler(func=lambda m: m.text == '🎨 Картинка')
def image_prompt(m):
    msg = bot.send_message(m.chat.id, "🎨 Опиши картинку:")
    bot.register_next_step_handler(msg, image_create)


def image_create(m):
    wait = bot.send_message(m.chat.id, "🎨 Создаю... (до 30 сек)")
    img = generate_image_simple(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    
    if img:
        bot.send_photo(m.chat.id, img, caption=f"🎨 {m.text}")
    else:
        bot.send_message(m.chat.id, "❌ Не удалось создать картинку")


# ========== ФИЛЬМ ==========

@bot.message_handler(func=lambda m: m.text == '🎬 Фильм')
def movie_prompt(m):
    msg = bot.send_message(m.chat.id, "🎬 Настроение?")
    bot.register_next_step_handler(msg, movie_answer)


def movie_answer(m):
    bot.send_message(m.chat.id, get_movie(m.text))


# ========== ФОТО ==========

@bot.message_handler(func=lambda m: m.text == '📸 Фото')
def photo_menu(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📤 Отправить фото', '🔙 Главное меню')
    bot.send_message(m.chat.id, "📸 Отправь фото:", reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('🎭 Мем', callback_data='meme'),
        types.InlineKeyboardButton('🗜 Сжать', callback_data='compress')
    )
    
    sent = bot.reply_to(m, "✅ Что сделать?", reply_markup=markup)
    
    photo_buttons_map[sent.message_id] = {
        'photo_id': m.message_id,
        'buttons_id': sent.message_id
    }


@bot.callback_query_handler(func=lambda c: True)
def photo_callback(c):
    data = photo_buttons_map.get(c.message.message_id)
    if not data:
        bot.answer_callback_query(c.id, "❌ Ошибка")
        return
    
    if c.data == 'meme':
        msg = bot.send_message(c.message.chat.id, "📝 Текст (верх | низ):")
        bot.register_next_step_handler(msg, meme_create, c.message)
    
    elif c.data == 'compress':
        file = bot.get_file(data['photo_id'])
        img = bot.download_file(file.file_path)
        compressed = compress(img)
        bot.send_photo(c.message.chat.id, compressed, caption="🗜 Сжато")
    
    bot.answer_callback_query(c.id)


def meme_create(m, original):
    data = photo_buttons_map.get(original.message_id)
    if not data:
        bot.send_message(m.chat.id, "❌ Ошибка")
        return
    
    parts = m.text.split('|')
    top = parts[0].strip() if parts else ''
    bottom = parts[1].strip() if len(parts) > 1 else ''
    
    file = bot.get_file(data['photo_id'])
    img = bot.download_file(file.file_path)
    meme = make_meme(img, top, bottom)
    
    bot.send_photo(m.chat.id, meme, caption="🎉 Мем готов!")


# ========== КУРСЫ ==========

@bot.message_handler(func=lambda m: m.text == '💰 Курсы')
def currency_handler(m):
    wait = bot.send_message(m.chat.id, "⏳ Получаю...")
    cur = get_currency()
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, cur, parse_mode='HTML')


# ========== ПОГОДА ==========

@bot.message_handler(func=lambda m: m.text == '🌤 Погода')
def weather_prompt(m):
    msg = bot.send_message(m.chat.id, "🌍 Город:")
    bot.register_next_step_handler(msg, weather_answer)


def weather_answer(m):
    wait = bot.send_message(m.chat.id, "⏳ Получаю...")
    w = get_weather(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, w, parse_mode='HTML')


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
    bot.register_next_step_handler(msg, translate_text)


def translate_text(m):
    wait = bot.send_message(m.chat.id, "⏳ Перевожу...")
    dest = user_data.get(m.chat.id, 'en')
    trans = translate(m.text, dest)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, f"🔤 {trans}")


# ========== ПОЗЫВНОЙ ==========

@bot.message_handler(func=lambda m: m.text == '🎯 Позывной')
def callsign_prompt(m):
    msg = bot.send_message(m.chat.id, "🎯 Слово:")
    bot.register_next_step_handler(msg, callsign_answer)


def callsign_answer(m):
    cs = callsign(m.text)
    text = "🎯 <b>Позывные:</b>\n\n" + "\n".join(cs)
    bot.send_message(m.chat.id, text, parse_mode='HTML')


# ========== ПОМОЩЬ ==========

@bot.message_handler(func=lambda m: m.text == '❓ Помощь')
def help_handler(m):
    text = "🤖 DeepSeek - любой вопрос\n"
    text += "🎨 Картинка - создание\n"
    text += "🎬 Фильм - по настроению\n"
    text += "📸 Фото - мемы, сжатие\n"
    text += "💰 Курсы - онлайн\n"
    text += "🌤 Погода - в любом городе\n"
    text += "🔤 Перевод - текста\n"
    text += "🎯 Позывной - генератор"
    bot.send_message(m.chat.id, text)


@bot.message_handler(func=lambda m: m.text == '🔙 Главное меню')
def back_to_menu(m):
    start(m)


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("🤖 DeepSeek: активен")
    print("🎨 Генерация: активна")
    print("📸 Фото: мемы и сжатие")
    print("=" * 50)
    
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
