import telebot as tb
from telebot import types
import requests
import time
import random
import urllib.parse
from datetime import datetime

# ========== НАСТРОЙКИ ==========
TOKEN = "8649201126:AAH8XA628lkSP9CLHukCcKJuo8CJr_cv2LM"
bot = tb.TeleBot(TOKEN)

# Хранилище для фото
photos = {}


# ========== 1. DEEPSEEK (РАБОТАЕТ) ==========

def ask_deepseek(q):
    try:
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-d838f69da7794f3998464fd7ead477b9"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Ты умный ассистент. Отвечай кратко и по делу."},
                    {"role": "user", "content": q}
                ],
                "temperature": 0.8
            },
            timeout=15
        )
        return r.json()['choices'][0]['message']['content'] if r.status_code == 200 else "❌ Ошибка"
    except:
        return f"❌ Не могу ответить сейчас"


# ========== 2. КАРТИНКИ (РАБОТАЕТ) ==========

def gen_image(prompt):
    try:
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
        r = requests.get(url, params={"width": 1024, "height": 1024, "nologo": "true"}, timeout=30)
        return r.content if r.status_code == 200 else None
    except:
        return None


# ========== 3. КУРСЫ (РАБОТАЕТ) ==========

def get_curs():
    try:
        r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        if r.status_code == 200:
            d = r.json()['Valute']
            return f"💰 USD: {d['USD']['Value']:.2f} ₽\n💶 EUR: {d['EUR']['Value']:.2f} ₽"
    except:
        return "❌ Курсы временно недоступны"


# ========== 4. ПОГОДА (РАБОТАЕТ) ==========

def get_pogoda(city):
    try:
        # Координаты
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
        if not geo.get('results'):
            return f"❌ Город {city} не найден"
        
        lat = geo['results'][0]['latitude']
        lon = geo['results'][0]['longitude']
        name = geo['results'][0]['name']
        
        # Погода
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        t = w['current_weather']['temperature']
        
        return f"🌍 {name}\n🌡 {t}°C"
    except:
        return "❌ Ошибка погоды"


# ========== 5. ПЕРЕВОД (РАБОТАЕТ) ==========

def perevod(text, lang='en'):
    try:
        r = requests.get(f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={lang}&dt=t&q={urllib.parse.quote(text)}")
        return r.json()[0][0][0] if r.status_code == 200 else "❌ Ошибка"
    except:
        return "❌ Ошибка"


# ========== 6. ФИЛЬМЫ ==========

def film(mood):
    films = {
        "веселый": "🎬 1+1 (2011)",
        "грустный": "🎬 Побег из Шоушенка (1994)",
        "романтика": "🎬 500 дней лета (2009)",
        "ужасы": "🎬 Заклятие (2013)",
        "фантастика": "🎬 Начало (2010)"
    }
    for k in films:
        if k in mood.lower():
            return films[k]
    return "🎬 1+1 (2011)"


# ========== 7. ПОЗЫВНОЙ ==========

def poziv(word):
    pre = ["Тихий", "Быстрый", "Дикий", "Мудрый", "Смелый"]
    suf = ["Волк", "Лис", "Медведь", "Орёл", "Сокол"]
    return [
        f"🎖 {random.choice(pre)} {word.title()}",
        f"🎖 {word.title()} {random.choice(suf)}",
        f"🎖 {random.choice(pre)} {random.choice(suf)}"
    ]


# ========== 8. ФОТО (МЕМЫ) ==========

def make_meme(img, top, bottom):
    try:
        from PIL import Image, ImageDraw
        import io
        
        image = Image.open(io.BytesIO(img))
        draw = ImageDraw.Draw(image)
        w, h = image.size
        
        if top:
            draw.text((w//2, 20), top, fill="white", anchor="mt")
        if bottom:
            draw.text((w//2, h-30), bottom, fill="white", anchor="mb")
        
        out = io.BytesIO()
        image.save(out, format='JPEG')
        return out.getvalue()
    except:
        return img


# ========== КОМАНДЫ ==========

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btns = [
        '🤖 DeepSeek', '🎨 Картинка', '🎬 Фильм', 
        '📸 Фото', '💰 Курсы', '🌤 Погода', 
        '🔤 Перевод', '🎯 Позывной'
    ]
    markup.add(*[types.KeyboardButton(b) for b in btns])
    
    bot.send_message(m.chat.id, 
        f"👋 Привет, {m.from_user.first_name}!\n\n"
        "🤖 DeepSeek - любой вопрос\n"
        "🎨 Картинка - создай изображение\n"
        "📸 Фото - мемы\n"
        "💰 Курсы - валюты", 
        reply_markup=markup)


# DeepSeek
@bot.message_handler(func=lambda m: m.text == '🤖 DeepSeek')
def d1(m):
    msg = bot.send_message(m.chat.id, "❓ Вопрос:")
    bot.register_next_step_handler(msg, d2)

def d2(m):
    wait = bot.send_message(m.chat.id, "⏳ Думаю...")
    ans = ask_deepseek(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    bot.send_message(m.chat.id, ans)


# Картинки
@bot.message_handler(func=lambda m: m.text == '🎨 Картинка')
def i1(m):
    msg = bot.send_message(m.chat.id, "🎨 Опиши:")
    bot.register_next_step_handler(msg, i2)

def i2(m):
    wait = bot.send_message(m.chat.id, "⏳ Генерирую...")
    img = gen_image(m.text)
    bot.delete_message(m.chat.id, wait.message_id)
    if img:
        bot.send_photo(m.chat.id, img)
    else:
        bot.send_message(m.chat.id, "❌ Не получилось")


# Фото
@bot.message_handler(func=lambda m: m.text == '📸 Фото')
def f1(m):
    msg = bot.send_message(m.chat.id, "📸 Отправь фото:")
    bot.register_next_step_handler(msg, f2)

def f2(m):
    if not m.photo:
        bot.send_message(m.chat.id, "❌ Это не фото")
        return
    
    bot.send_message(m.chat.id, "📝 Напиши текст для мема (верх | низ):")
    photos[m.chat.id] = m.photo[-1].file_id


@bot.message_handler(func=lambda m: m.chat.id in photos)
def f3(m):
    file_id = photos.pop(m.chat.id, None)
    if not file_id:
        return
    
    parts = m.text.split('|')
    top = parts[0].strip() if parts else ''
    bottom = parts[1].strip() if len(parts) > 1 else ''
    
    file = bot.get_file(file_id)
    img = bot.download_file(file.file_path)
    meme = make_meme(img, top, bottom)
    
    bot.send_photo(m.chat.id, meme, caption="🎉 Мем готов!")


# Курсы
@bot.message_handler(func=lambda m: m.text == '💰 Курсы')
def c1(m):
    bot.send_message(m.chat.id, get_curs())


# Погода
@bot.message_handler(func=lambda m: m.text == '🌤 Погода')
def p1(m):
    msg = bot.send_message(m.chat.id, "🌍 Город:")
    bot.register_next_step_handler(msg, p2)

def p2(m):
    bot.send_message(m.chat.id, get_pogoda(m.text))


# Перевод
@bot.message_handler(func=lambda m: m.text == '🔤 Перевод')
def t1(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('🇬🇧 На английский', '🇷🇺 На русский')
    msg = bot.send_message(m.chat.id, "🌐 Направление:", reply_markup=markup)
    bot.register_next_step_handler(msg, t2)

def t2(m):
    lang = 'en' if '🇬🇧' in m.text else 'ru'
    msg = bot.send_message(m.chat.id, "📝 Текст:")
    bot.register_next_step_handler(msg, lambda x: t3(x, lang))

def t3(m, lang):
    bot.send_message(m.chat.id, f"🔤 {perevod(m.text, lang)}")


# Фильм
@bot.message_handler(func=lambda m: m.text == '🎬 Фильм')
def mov1(m):
    msg = bot.send_message(m.chat.id, "🎬 Настроение?")
    bot.register_next_step_handler(msg, mov2)

def mov2(m):
    bot.send_message(m.chat.id, film(m.text))


# Позывной
@bot.message_handler(func=lambda m: m.text == '🎯 Позывной')
def poz1(m):
    msg = bot.send_message(m.chat.id, "🎯 Слово:")
    bot.register_next_step_handler(msg, poz2)

def poz2(m):
    res = poziv(m.text)
    bot.send_message(m.chat.id, "\n".join(res))


# ========== ЗАПУСК ==========

if __name__ == "__main__":
    print("✅ БОТ ГОТОВ!")
    print("🤖 DeepSeek - работает")
    print("🎨 Картинки - работают")
    print("📸 Фото - работает")
    print("💰 Курсы - работают")
    
    while True:
        try:
            bot.polling(non_stop=True)
        except:
            time.sleep(5)

