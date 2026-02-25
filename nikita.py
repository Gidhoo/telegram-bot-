import telebot as tb
from datetime import datetime
from telebot import types
import time
import requests
import random
import urllib.parse
import io
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont

# ========== HTTP СЕРВЕР ДЛЯ RENDER ==========

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Telegram Bot is running!</h1>")
        self.wfile.write(b"<p>Bot: @NikitaPriorikPlakiPlakiTestbot</p>")
        self.wfile.write(b"<p>Status: Active</p>")
    
    def log_message(self, format, *args):
        pass  # Отключаем логи сервера

def run_http_server():
    """Запускает HTTP сервер для проверки Render"""
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    print(f"🌐 HTTP сервер запущен на порту {port}")
    print(f"🌐 URL: http://0.0.0.0:{port}")
    server.serve_forever()

# ========== НОВЫЙ ТОКЕН ==========
TOKEN = "8649201126:AAH8XA628lkSP9CLHukCcKJuo8CJr_cv2LM"  # НОВЫЙ ТОКЕН!
YOUR_CHAT_ID = 1551325264
DEEPSEEK_KEY = "sk-d838f69da7794f3998464fd7ead477b9"

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = tb.TeleBot(TOKEN)
user_data = {}
photo_buttons_map = {}


# ========== DEEPSEEK AI ==========

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
        elif response.status_code == 401:
            return "❌ Ошибка авторизации DeepSeek. Проверьте API ключ."
        elif response.status_code == 429:
            return "❌ Слишком много запросов к DeepSeek. Попробуйте позже."
        else:
            return f"❌ Ошибка API DeepSeek: {response.status_code}"
            
    except Exception as e:
        return f"❌ Ошибка соединения с DeepSeek: {e}"


# ========== ГЕНЕРАЦИЯ КАРТИНОК ==========

def generate_image_simple(prompt):
    """Простая генерация картинок"""
    try:
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
            return None
            
    except Exception as e:
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
            
            return f"💰 <b>Курсы ЦБ РФ</b>\n\n🇺🇸 USD: {usd:.2f} ₽\n🇪🇺 EUR: {eur:.2f} ₽"
    except:
        pass
    return "❌ Курсы временно недоступны"


# ========== ПОГОДА ==========

def get_weather(city):
    """Погода в городе"""
    try:
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
        
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_r = requests.get(w_url, timeout=5)
        
        if w_r.status_code != 200:
            return f"❌ Не удалось получить погоду"
        
        w_data = w_r.json()['current_weather']
        temp = w_data['temperature']
        
        return f"🌍 <b>{name}</b>\n\n🌡 {temp}°C"
        
    except:
        return "❌ Ошибка погоды"


# ========== ПЕРЕВОД ==========

def translate(text, dest='en'):
    """Перевод текста"""
    try:
        enc = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={dest}&dt=t&q={enc}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            res = r.json()
            return res[0][0][0]
    except:
        pass
    return "❌ Ошибка перевода"


# ========== ФИЛЬМЫ ==========

def get_movie(mood):
    """Рекомендация фильма"""
    movies = {
        "веселый": "🎬 1+1",
        "грустный": "🎬 Побег из Шоушенка",
        "романтичный": "🎬 500 дней лета",
        "страшный": "🎬 Заклятие",
        "фантастика": "🎬 Начало",
    }
    for k in movies:
        if k in mood.lower():
            return movies[k]
    return "🎬 1+1"


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
        
        if top:
            draw.text((w//2, 10), top, fill="white", anchor="mt")
        if bottom:
            draw.text((w//2, h-30), bottom, fill="white", anchor="mb")
        
        out = io.BytesIO()
        img.save(out, format='JPEG')
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
        types.KeyboardButton('🎯 Позывной')
    )
    
    bot.send_message(m.chat.id, f"👋 Привет, {m.from_user.first_name}!", reply_markup=markup)


# ========== DEEPSEEK ==========

@bot.message_handler(func=lambda m: m.text == '🤖 DeepSeek')
def deepseek_prompt(m):
    msg = bot.send_message(m.chat.id, "❓ Вопрос:")
    bot.register_next_step_handler(msg, deepseek_answer)


def deepseek_answer(m):
    ans = ask_deepseek(m.text)
    bot.send_message(m.chat.id, ans)


# ========== КАРТИНКИ ==========

@bot.message_handler(func=lambda m: m.text == '🎨 Картинка')
def image_prompt(m):
    msg = bot.send_message(m.chat.id, "🎨 Опиши:")
    bot.register_next_step_handler(msg, image_create)


def image_create(m):
    msg = bot.send_message(m.chat.id, "⏳ Создаю...")
    img = generate_image_simple(m.text)
    bot.delete_message(m.chat.id, msg.message_id)
    
    if img:
        bot.send_photo(m.chat.id, img)
    else:
        bot.send_message(m.chat.id, "❌ Ошибка")


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
    bot.send_message(m.chat.id, "📸 Отправь фото:")


@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('🎭 Мем', callback_data='meme'),
        types.InlineKeyboardButton('🗜 Сжать', callback_data='compress')
    )
    
    photo_buttons_map[m.message_id] = m.photo[-1].file_id
    bot.reply_to(m, "✅ Что сделать?", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: True)
def photo_callback(c):
    file_id = photo_buttons_map.get(c.message.reply_to_message.message_id)
    if not file_id:
        bot.answer_callback_query(c.id, "❌ Ошибка")
        return
    
    if c.data == 'meme':
        msg = bot.send_message(c.message.chat.id, "📝 Текст (верх | низ):")
        bot.register_next_step_handler(msg, meme_create, file_id)
    
    elif c.data == 'compress':
        file = bot.get_file(file_id)
        img = bot.download_file(file.file_path)
        compressed = img
        bot.send_photo(c.message.chat.id, compressed)
    
    bot.answer_callback_query(c.id)


def meme_create(m, file_id):
    parts = m.text.split('|')
    top = parts[0].strip() if parts else ''
    bottom = parts[1].strip() if len(parts) > 1 else ''
    
    file = bot.get_file(file_id)
    img = bot.download_file(file.file_path)
    meme = make_meme(img, top, bottom)
    
    bot.send_photo(m.chat.id, meme, caption="🎉 Мем готов!")


# ========== КУРСЫ ==========

@bot.message_handler(func=lambda m: m.text == '💰 Курсы')
def currency_handler(m):
    bot.send_message(m.chat.id, get_currency(), parse_mode='HTML')


# ========== ПОГОДА ==========

@bot.message_handler(func=lambda m: m.text == '🌤 Погода')
def weather_prompt(m):
    msg = bot.send_message(m.chat.id, "🌍 Город:")
    bot.register_next_step_handler(msg, weather_answer)


def weather_answer(m):
    bot.send_message(m.chat.id, get_weather(m.text), parse_mode='HTML')


# ========== ПЕРЕВОД ==========

@bot.message_handler(func=lambda m: m.text == '🔤 Перевод')
def translate_prompt(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('🇬🇧 На английский', '🇷🇺 На русский')
    msg = bot.send_message(m.chat.id, "🌐 Направление:", reply_markup=markup)
    bot.register_next_step_handler(msg, translate_lang)


def translate_lang(m):
    lang = 'en' if '🇬🇧' in m.text else 'ru'
    msg = bot.send_message(m.chat.id, "📝 Текст:")
    bot.register_next_step_handler(msg, lambda x: translate_text(x, lang))


def translate_text(m, lang):
    bot.send_message(m.chat.id, f"🔤 {translate(m.text, lang)}")


# ========== ПОЗЫВНОЙ ==========

@bot.message_handler(func=lambda m: m.text == '🎯 Позывной')
def callsign_prompt(m):
    msg = bot.send_message(m.chat.id, "🎯 Слово:")
    bot.register_next_step_handler(msg, callsign_answer)


def callsign_answer(m):
    cs = callsign(m.text)
    bot.send_message(m.chat.id, "\n".join(cs))


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print(f"🔑 Токен: {TOKEN[:15]}...")
    print("=" * 50)
    print("🌐 Запускаем HTTP сервер для Render...")
    
    # Запускаем HTTP сервер в отдельном потоке
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()
    
    print("🤖 Запускаем Telegram бота...")
    print("=" * 50)
    
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
