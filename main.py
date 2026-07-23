import os
import threading
import time
import re
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
from flask import Flask

# ১. টেলিগ্রাম বট টোকেন সেটআপ
API_TOKEN = os.environ.get("BOT_TOKEN") 
bot = telebot.TeleBot(API_TOKEN)

# ২. ফ্রি নম্বর সাইটের তালিকা (যেকোনো দেশের নম্বরের জন্য)
SITES = {
    "s1": "https://receivesmsfast.com",
    "s2": "https://sms-receive.net",
    "s3": "https://receive-sms.cc",
    "s4": "https://temporary-phone-number.com"
}

# ৩. ওয়েবসাইট থেকে যেকোনো দেশের আসল নম্বর স্ক্র্যাপ করার ফাংশন
def fetch_any_live_number():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    for site_key, url in SITES.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # আন্তর্জাতিক ফরম্যাটের মোবাইল নম্বর খোঁজার রেগুলার এক্সপ্রেশন প্যাটার্ন (+ সহ বা ছাড়া)
                numbers = re.findall(r'\+?\d{10,15}', soup.get_text())
                for num in numbers:
                    # ডামি বা ফেক ধারাবাহিক ০ এবং ১ বিশিষ্ট নম্বর ফিল্টার করা
                    if "000000" not in num and "111111" not in num:
                        if not num.startswith('+'):
                            num = '+' + num
                        return num, site_key
        except:
            continue
    return None, None

# ৪. ওটিপি স্ক্র্যাপ করার উন্নত ফাংশন
def get_live_otp(phone_number, site_key):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    clean_number = phone_number.replace("+", "").strip()
    
    url_map = {
        "s1": f"https://receivesmsfast.com{clean_number}",
        "s2": f"https://sms-receive.net{clean_number}",
        "s3": f"https://receive-sms.cc{clean_number}",
        "s4": f"https://temporary-phone-number.com{clean_number}"
    }
    
    url = url_map.get(site_key, f"https://receivesmsfast.com{clean_number}")
    
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

# ৫. টেলিগ্রাম বটের কমান্ড হ্যান্ডলারসমূহ (সব বাটনসহ)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("📱 Get Number")
    btn2 = types.KeyboardButton("📊 Server Status")
    btn3 = types.KeyboardButton("🔐 2FA ONLINE")
    btn4 = types.KeyboardButton("🔄 Refresh Bot")
    btn5 = types.KeyboardButton("ℹ️ Support")
    
    markup.add(btn1)
    markup.add(btn2, btn3)
    markup.add(btn4, btn5)
    
    bot.send_message(message.chat.id, "👋 আমাদের বটে স্বাগতম! নিচের বাটনগুলো ব্যবহার করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Support")
def support_info(message):
    bot.send_message(message.chat.id, "📞 যেকোনো সমস্যায় আমাদের অ্যাডমিনের সাথে যোগাযোগ করুন: @Shar_iyar")

@bot.message_handler(func=lambda message: message.text == "📊 Server Status")
def server_status(message):
    bot.send_message(message.chat.id, "🟢 সকল সার্ভার সচল আছে (Server is Online).")

@bot.message_handler(func=lambda message: message.text == "🔐 2FA ONLINE")
def two_factor_info(message):
    bot.send_message(message.chat.id, "🛡️ ২-স্টেপ ভেরিফিকেশন (2FA) সার্ভিসটি এই মুহূর্তে চালু আছে।")

@bot.message_handler(func=lambda message: message.text == "🔄 Refresh Bot")
def refresh_bot(message):
    bot.send_message(message.chat.id, "🔄 বট রিফ্রেশ করা হয়েছে। নতুন করে ট্রাই করুন।")

@bot.message_handler(func=lambda message: message.text == "📱 Get Number")
def get_number_handler(message):
    bot.send_message(message.chat.id, "🔄 আমাদের সার্ভার থেকে লাইভ নাম্বার সংগ্রহ করা হচ্ছে, একটু অপেক্ষা করুন...")
    
    real_number, site_key = fetch_any_live_number()
    
    if real_number:
        reply_text = (
            f"✅ **আপনার নাম্বার রেডি!**\n\n"
            f"📱 **নাম্বার:** `{real_number}`\n\n"
            f"💡 নাম্বারের ওপর চাপ দিলে অটো কপি হয়ে যাবে। এটি অ্যাপে বসিয়ে কোড পাঠান, তারপর নিচে Check OTP বাটনে চাপুন।"
        )
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton("📩 Check OTP", callback_data=f"check_{real_number}_{site_key}"))
        bot.send_message(message.chat.id, reply_text, reply_markup=inline_markup)
    else:
        bot.send_message(message.chat.id, "❌ দুঃখিত, এই মুহূর্তে ফ্রি ওয়েবসাইটগুলোতে কোনো সচল নম্বর পাওয়া যায়নি। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_otp(call):
    _, phone_number, site_key = call.data.split("_")
    bot.answer_callback_query(call.id, text="ওটিপি চেক করা হচ্ছে...")
    
    latest_sms = get_live_otp(phone_number, site_key)
    
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("🔄 Re-check OTP", callback_data=f"check_{phone_number}_{site_key}"))
    
    bot.send_message(call.message.chat.id, latest_sms, reply_markup=inline_markup)

# ৬. রেন্ডার সার্ভার সচল রাখার জন্য Flask ওয়েব সার্ভার
app = Flask(__name__)

@app.route('/')
def home():
    return "Online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ব্যাকগ্রাউন্ডে Flask এবং মেইন থ্রেডে বট চালানো
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
