import telebot
import requests
import re
import random
import os
from telebot import types
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from flask import Flask
from threading import Thread

# টোকেন রেন্ডার থেকে অটোমেটিক লোড হবে
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# সার্ভার সচল রাখার জন্য ফ্লাস্ক মেকানিজম
app = Flask('')
@app.route('/')
def home(): 
    return "Bot Server is Live!"

def run(): 
    bot_port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=bot_port)

def keep_alive(): 
    Thread(target=run).start()

# ৬টি ফ্রি ওটিপি সাইটের তালিকা
SMS_SITES = [
    {"url": "https://receive-sms-free.cc", "type": "site1"},
    {"url": "https://sms-receive.net", "type": "site2"},
    {"url": "https://receive-sms-online.info", "type": "site3"},
    {"url": "https://receive-smss.com", "type": "site4"},
    {"url": "https://freephonenum.com", "type": "site5"},
    {"url": "https://sms24.me", "type": "site6"}
]

def fetch_free_number():
    random.shuffle(SMS_SITES)
    headers = {"User-Agent": "Mozilla/5.0"}
    for site in SMS_SITES:
        try:
            res = requests.get(site["url"], headers=headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                if site["type"] == "site1":
                    lnk = soup.find('a', href=re.compile(r'/free-sms-phone-number/'))
                    if lnk: return re.sub(r'[^\d+]', '', lnk.text.strip()), lnk['href'], "site1"
                elif site["type"] == "site2":
                    lnk = soup.find('a', href=re.compile(r'/sms/'))
                    if lnk: return lnk.text.strip(), lnk['href'], "site2"
                elif site["type"] == "site3":
                    lnk = soup.find('a', href=re.compile(r'/phone-number/'))
                    if lnk: return re.sub(r'[^\d+]', '', lnk.text.strip()), lnk['href'], "site3"
                elif site["type"] == "site4":
                    lnk = soup.find('a', href=re.compile(r'/sms/'))
                    if lnk: return re.sub(r'[^\d+]', '', lnk.text.strip()), lnk['href'], "site4"
                elif site["type"] == "site5":
                    lnk = soup.find('a', href=re.compile(r'/us/|/ca/'))
                    if lnk: return lnk.text.strip(), lnk['href'], "site5"
                elif site["type"] == "site6":
                    lnk = soup.find('a', href=re.compile(r'/en/'))
                    if lnk: return lnk.text.strip(), lnk['href'], "site6"
        except Exception: 
            continue
    return None, None, None

def fetch_latest_otp(page_slug, site_type):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        if site_type == "site1":
            r = requests.get(f"https://receive-sms-free.cc{page_slug}", headers=headers, timeout=8)
            if r.status_code == 200: return BeautifulSoup(r.text, 'html.parser').find('div', class_='row border-bottom').text.strip()
        elif site_type == "site2":
            r = requests.get(f"https://sms-receive.net{page_slug}", headers=headers, timeout=8)
            if r.status_code == 200: return BeautifulSoup(r.text, 'html.parser').find_all('tr')[1].text.strip()
        elif site_type == "site3":
            r = requests.get(f"https://receive-sms-online.info{page_slug}", headers=headers, timeout=8)
            if r.status_code == 200: return BeautifulSoup(r.text, 'html.parser').find('div', class_='sms-message').text.strip()
        elif site_type == "site4":
            r = requests.get(f"https://receive-smss.com{page_slug}", headers=headers, timeout=8)
            if r.status_code == 200: return BeautifulSoup(r.text, 'html.parser').find_all('tr')[1].text.strip()
        elif site_type == "site5":
            r = requests.get(f"https://freephonenum.com{page_slug}", headers=headers, timeout=8)
            if r.status_code == 200: return BeautifulSoup(r.text, 'html.parser').find('div', class_='msg-row').text.strip()
        elif site_type == "site6":
            r = requests.get(f"https://sms24.me{page_slug}", headers=headers, timeout=8)
            if r.status_code == 200: return BeautifulSoup(r.text, 'html.parser').find('div', class_='msg-text').text.strip()
    except Exception: 
        pass
    return "No message found yet."

# বটের মূল কিবোর্ড বাটনগুলো
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_states[user_id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📱 Get Number", "🔄 Check OTP", "📊 Traffic", "🔐 2FA Online", "🛠 Support", "👥 Refer")
    bot.send_message(user_id, "👋 Welcome to SMS Zone Bot! Select an option below:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.chat.id
    text = message.text
    
    if user_states.get(user_id, {}).get("action") == "waiting_for_2fa_key":
        generate_2fa_otp(message)
        return
        
    if "Get Number" in text:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("📸 Instagram", callback_data="get_num_instagram")
        btn2 = types.InlineKeyboardButton("📘 Facebook", callback_data="get_num_facebook")
        btn3 = types.InlineKeyboardButton("🎵 TikTok", callback_data="get_num_tiktok")
        markup.add(btn1, btn2, btn3)
        bot.send_message(user_id, "🎯 **Select a Platform for Virtual Number:**", reply_markup=markup, parse_mode="Markdown")
        
    elif "Check OTP" in text:
        process_otp_check(user_id)
        
    elif "Traffic" in text:
        bot.send_message(user_id, "📊 **Current Traffic:**\n\n✅ Servers: Online\n🟢 Speed: Fast", parse_mode="Markdown")
        
    elif "2FA Online" in text:
        user_states[user_id] = {"action": "waiting_for_2fa_key"}
        bot.send_message(user_id, "🔐 Please send your **2FA Secret Key** or **Link**:", parse_mode="Markdown")
        
    elif "Support" in text:
        bot.send_message(user_id, "🛠 **Support Contact:** @Shar_iyar")
        
    elif "Refer" in text:
        bot.send_message(user_id, f"👥 **Refer Link:**\nhttps://t.me{bot.get_me().username}?start={user_id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_num_"))
def handle_platform_selection(call):
    user_id = call.message.chat.id
    platform = call.data.replace("get_num_", "").capitalize()
    bot.answer_callback_query(call.id, "Searching number...")
    bot.send_message(user_id, f"⏳ Fetching number for **{platform}**. Please wait...", parse_mode="Markdown")
    
    num, slug, stype = fetch_free_number()
    if num and slug and stype:
        user_states[user_id] = {"page_slug": slug, "site_type": stype, "number": num}
        bot.send_message(user_id, f"📱 **Your Number:** `{num}`\n\nSend OTP, then click the **Check OTP** button from menu.", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ No numbers available at the moment. Try again later.")

def process_otp_check(user_id):
    if user_id in user_states and "page_slug" in user_states[user_id]:
        slug = user_states[user_id]["page_slug"]
        stype = user_states[user_id]["site_type"]
        bot.send_message(user_id, "⏳ Checking for incoming OTP...")
        raw = fetch_latest_otp(slug, stype)
        code = re.findall(r'\b\d{4,6}\b', raw)
        if code:
            bot.send_message(user_id, f"💬 **Your OTP Code:** `{code}`\n\n📜 **Full Message:**\n{raw}", parse_mode="Markdown")
        else:
            bot.send_message(user_id, f"ℹ️ OTP code not found yet. Latest SMS:\n\n{raw}")
    else:
        bot.send_message(user_id, "⚠️ No active session found. Please click **Get Number** first.")

def generate_2fa_otp(message):
    user_id = message.chat.id
    input_text = message.text.strip()
    secret_key = None
    try:
        if input_text.startswith("otpauth://"):
            p = parse_qs(urlparse(input_text).query)
            if 'secret' in p: secret_key = p['secret'][0].upper()
        else:
            secret_key = input_text.replace(" ", "").upper()
            
        if secret_key:
            totp = pyotp.TOTP(secret_key)
            bot.send_message(user_id, f"🔐 **Your 2FA Code:** `{totp.now()}`", parse_mode="Markdown")
        else:
            raise ValueError()
    except Exception:
        bot.send_message(user_id, "❌ Invalid 2FA Secret Key or Link!")
    user_states[user_id] = {}

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling() 
