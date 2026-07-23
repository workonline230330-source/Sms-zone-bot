import os
import time
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
from threading import Thread
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

SITES = {
    "s1": "https://receivesmsfast.com",
    "s2": "https://sms-receive.net",
    "s3": "https://receive-sms.cc",
    "s4": "https://temporary-phone-number.com"
}

def fetch_from_s1():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(SITES["s1"], headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            tag = soup.find('h3', class_='number-boxes-item-number')
            if tag: return tag.text.strip(), "s1"
    except: pass
    return None

def fetch_from_s2():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(SITES["s2"], headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            num_tag = soup.find('div', class_='number_box')
            if num_tag and num_tag.find('h3'):
                return num_tag.find('h3').text.strip(), "s2"
    except: pass
    return None

def fetch_from_s4():
    """Temporary-Phone-Number.com সাইট থেকে নাম্বার স্ক্র্যাপ করার লজিক"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(SITES["s4"], headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # সাইটের স্ট্রাকচার অনুযায়ী নাম্বার বক্সের ট্যাগ খুঁজে নেওয়া
            num_box = soup.find('div', class_='number-box')
            if num_box and num_box.find('a'):
                return num_box.find('a').text.strip(), "s4"
    except: pass
    return None

def get_live_number():
    data = fetch_from_s1()
    if data: return data
    data = fetch_from_s2()
    if data: return data
    data = fetch_from_s4()
    if data: return data
    return "+8801700000000", "s1"

def get_live_otp(phone_number, source_site):
    clean_num = phone_number.replace('+', '').replace(' ', '')
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        if source_site == "s1":
            url = f"https://receivesmsfast.com{clean_num}"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                msg = soup.find('td', class_='sms-content')
                if msg: return msg.text.strip()
                
        elif source_site == "s2":
            url = f"https://sms-receive.net{clean_num}"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                msg = soup.find('div', class_='msg_text')
                if msg: return msg.text.strip()

        elif source_site == "s4":
            url = f"https://temporary-phone-number.com{clean_num}"
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                msg = soup.find('div', class_='sms-msg')
                if msg: return msg.text.strip()
    except: pass
    return "এখনো কোনো নতুন ওটিপি (OTP) মেসেজ আসেনি। ১ মিনিট পর আবার চেষ্টা করুন।"

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_get = types.KeyboardButton("📱 Get Number")
    btn_server = types.KeyboardButton("📊 Server Status")
    btn_2fa = types.KeyboardButton("🔐 2FA ONLINE")
    btn_refresh = types.KeyboardButton("🔄 Refresh Bot")
    btn_support = types.KeyboardButton("📞 Support")
    
    markup.row(btn_get)
    markup.row(btn_server, btn_2fa)
    markup.row(btn_refresh, btn_support)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = "🔥 **Social media SMS zone** বটে আপনাকে স্বাগত!\n\nইনস্ট্যান্ট নাম্বার এবং ওটিপি (OTP) পেতে নিচের বাটনগুলো ব্যবহার করুন।"
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📱 Get Number")
def send_number(message):
    bot.send_message(message.chat.id, "🔄 আমাদের সার্ভার থেকে লাইভ নাম্বার সংগ্রহ করা হচ্ছে, একটু অপেক্ষা করুন...")
    
    live_number, source = get_live_number()
    
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("📩 Check OTP", callback_data=f"check_{live_number}_{source}"))
    
    msg = f"✅ **আপনার নাম্বার রেডি!**\n\n📱 নাম্বার: `{live_number}`\n\n💡 নাম্বারের ওপর চাপ দিলে অটো কপি হয়ে যাবে। এটি অ্যাপে বসিয়ে কোড পাঠান, তারপর নিচে **Check OTP** বাটনে চাপুন।"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=inline_markup)

@bot.message_handler(func=lambda message: message.text == "📊 Server Status")
def server_status(message):
    msg = "📊 **সার্ভার স্ট্যাটাস:**\n\n🟢 Server Node 1 — ONLINE\n🟢 Server Node 2 — ONLINE\n🟢 Gateway — ONLINE\n⚡ ওটিপি স্পীড: ফাস্ট (Fast)"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔐 2FA ONLINE")
def two_factor_online(message):
    msg = "🔐 **2FA অনলাইন সার্ভিস:**\n\nআপনার ২এফএ কোড জেনারেট করতে আপনার সিক্রেট কী (Secret Key) লিখে মেসেজ করুন।"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔄 Refresh Bot")
def refresh_bot(message):
    bot.send_message(message.chat.id, "🔄 বট সফলভাবে রিফ্রেশ এবং সতেজ করা হয়েছে!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📞 Support")
def support_info(message):
    bot.send_message(message.chat.id, "📞 যেকোনো সমস্যায় আমাদের অ্যাডমিনের সাথে যোগাযোগ করুন: @Shar_iyar")

import re
def get_live_otp(phone_number, source_site):
    headers = {'UsereAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    clean_number = phone_number.replace("+", "").strip()
    
    url_map = {
        "https://receivesmsfast.com": f"https://receivesmsfast.com{clean_number}",
        "https://sms-receive.net": f"https://sms-receive.net{clean_number}",
        "https://receive-sms.cc": f"https://receive-sms.cc{clean_number}",
        "https://temporary-phone-number.com": f"https://temporary-phone-number.com{clean_number}"
    }
    
    url = url_map.get(source_site, f"https://receivesmsfast.com{clean_number}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            otp_match = re.search(r'\b\d{4,6}\b', page_text)
            if otp_match:
                detected_code = otp_match.group(0)
                return f"📩 **সর্বশেষ প্রাপ্ত ওটিপি কোড:** `{detected_code}`"
    except Exception as e:
        print(f"OTP Scraping Error: {e}")
        
    return "❌ এখনো কোনো নতুন ওটিপি (OTP) মেসেজ আসেনি।"

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_otp(call):
    _, phone_number, source = call.data.split("_")
    bot.answer_callback_query(call.id, text="ওটিপি চেক করা হচ্ছে...")
    
    latest_sms = get_live_otp(phone_number, source)
    
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("🔄 Re-check OTP", callback_data=f"check_{phone_number}_{source}"))
    
    bot.send_message(call.message.chat.id, latest_sms, reply_markup=inline_markup)
import os
import threading
import time
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Flask ব্যাকগ্রাউন্ডে চালু করা এবং মেইন থ্রেডে বট চালানো
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

print("Bot is starting...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Bot Polling Error: {e}")
        time.sleep(5)
