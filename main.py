import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import re
import random
import pyotp
from urllib.parse import urlparse, parse_qs
from flask import Flask
from threading import Thread
import os

# Render এর Environment Variable থেকে টোকেনটি নেওয়া হচ্ছে
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# ইউজারের ডাটা এবং স্টেট ধরে রাখার জন্য খালি ডিকশনারি (এটি অত্যন্ত জরুরি)
user_states = {}

# ----------------- FLASK SERVER (FOR UPTIME ROBOT) -----------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running safely on Render free tier!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------- FREE SMS SITES SCRAPER -----------------
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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for site in SMS_SITES:
        try:
            response = requests.get(site["url"], headers=headers, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if site["type"] == "site1":
                    links = soup.find_all('a', href=re.compile(r'/free-sms-phone-number/'))
                    if links:
                        return re.sub(r'[^\d+]', '', links[0].text.strip()), links[0]['href'], "site1"
                        
                elif site["type"] == "site2":
                    links = soup.find_all('a', href=re.compile(r'/sms/'))
                    if links:
                        return links[0].text.strip(), links[0]['href'], "site2"
                        
                elif site["type"] == "site3":
                    links = soup.find_all('a', href=re.compile(r'/phone-number/'))
                    if links:
                        return re.sub(r'[^\d+]', '', links[0].text.strip()), links[0]['href'], "site3"
                        
                elif site["type"] == "site4":
                    links = soup.find_all('a', href=re.compile(r'/sms/'))
                    if links:
                        return re.sub(r'[^\d+]', '', links[0].text.strip()), links[0]['href'], "site4"
                        
                elif site["type"] == "site5":
                    links = soup.find_all('a', href=re.compile(r'/us/|/ca/'))
                    if links:
                        return links[0].text.strip(), links[0]['href'], "site5"
                        
                elif site["type"] == "site6":
                    links = soup.find_all('a', href=re.compile(r'/en/'))
                    if links:
                        return links[0].text.strip(), links[0]['href'], "site6"
        except Exception:
            continue
            
    return None, None, None

def fetch_latest_otp(page_slug, site_type):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        if site_type == "site1":
            url = f"https://receive-sms-free.cc{page_slug}"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                msg = BeautifulSoup(res.text, 'html.parser').find('div', class_='row border-bottom')
                return msg.text.strip() if msg else "No messages found"
                    
        elif site_type == "site2":
            url = f"https://sms-receive.net{page_slug}"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                rows = BeautifulSoup(res.text, 'html.parser').find_all('tr')
                return rows[0].text.strip() if len(rows) > 0 else "No messages found"
                    
        elif site_type == "site3":
            url = f"https://receive-sms-online.info{page_slug}"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                msg = BeautifulSoup(res.text, 'html.parser').find('div', class_='sms-message')
                return msg.text.strip() if msg else "No messages found"
                
        elif site_type == "site4":
            url = f"https://receive-smss.com{page_slug}"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                rows = BeautifulSoup(res.text, 'html.parser').find_all('tr')
                return rows[0].text.strip() if len(rows) > 0 else "No messages found"
                
        elif site_type == "site5":
            url = f"https://freephonenum.com{page_slug}"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                msg = BeautifulSoup(res.text, 'html.parser').find('div', class_='msg-row')
                return msg.text.strip() if msg else "No messages found"
                
        elif site_type == "site6":
            url = f"https://sms24.me{page_slug}"
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                msg = BeautifulSoup(res.text, 'html.parser').find('div', class_='msg-text')
                return msg.text.strip() if msg else "No messages found"
    except Exception:
        pass
        
    return "No message found yet. Please try again."

# ----------------- TELEGRAM BOT COMMANDS & HANDLERS -----------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_states[user_id] = {} # সেশন ক্লিয়ার
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📱 Get Number")
    btn2 = types.KeyboardButton("🔄 Check OTP")
    btn3 = types.KeyboardButton("📊 Traffic")
    btn4 = types.KeyboardButton("🔐 2FA Online")
    btn5 = types.KeyboardButton("🛠 Support")
    btn6 = types.KeyboardButton("👥 Refer")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(user_id, "👋 Welcome to SMS Zone Bot! Select an option below:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.chat.id
    text = message.text

    # ২এফএ কি এর জন্য অপেক্ষা করলে এই টেক্সট প্রোসেস হবে
    if user_states.get(user_id, {}).get("action") == "waiting_for_2fa_key":
        generate_2fa_otp(message)
        return

    if "Get Number" in text:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_insta = types.InlineKeyboardButton("📸 Instagram", callback_data="get_number_instagram")
        btn_fb = types.InlineKeyboardButton("📘 Facebook", callback_data="get_number_facebook")
        btn_tiktok = types.InlineKeyboardButton("🎵 TikTok", callback_data="get_number_tiktok")
        markup.add(btn_insta, btn_fb, btn_tiktok)
        
        bot.send_message(user_id, "🎯 **Select a Platform for Virtual Number:**", reply_markup=markup, parse_mode="Markdown")

    elif "Check OTP" in text:
        process_otp_check(user_id)

    elif "Traffic" in text:
        bot.send_message(user_id, "📊 **Current Bot Traffic:**\n\n✅ Servers: Online\n🟢 Load: Normal\n🚀 Speed: Fast", parse_mode="Markdown")

    elif "2FA Online" in text:
        user_states[user_id] = {"action": "waiting_for_2fa_key"}
        bot.send_message(user_id, "🔐 Please send your **2FA Secret Key** or **otpauth:// Link**:", parse_mode="Markdown")

    elif "Support" in text:
        bot.send_message(user_id, "🛠 **Support Channel:**\n\nNeed help? Contact our support administrator: @Shar_iyar", parse_mode="Markdown")

    elif "Refer" in text:
        refer_link = f"https://t.me{bot.get_me().username}?start={user_id}"
        bot.send_message(user_id, f"👥 **Refer & Earn:**\n\nShare your referral link with friends:\n{refer_link}", parse_mode="Markdown")

# ----------------- CALLBACK AND LOGIC HANDLERS -----------------

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_number_"))
def handle_platform_selection(call):
    user_id = call.message.chat.id
    platform = call.data.replace("get_number_", "").capitalize()
    
    bot.answer_callback_query(call.id, f"Finding number for {platform}...")
    bot.send_message(user_id, f"⏳ Fetching a free virtual number for **{platform}**. Please wait...", parse_mode="Markdown")
    
    number, page_slug, site_type = fetch_free_number()
    
    if number and page_slug and site_type:
        user_states[user_id] = {"page_slug": page_slug, "site_type": site_type, "number": number, "platform": platform}
        bot.send_message(user_id, f"📱 **Your Number for {platform}:** `{number}`\n\nSend your OTP to this number, then click the **Check OTP** button from the menu.", parse_mode="Markdown")
    else:
        bot.send_message(user_id, f"❌ Sorry, no free numbers available for **{platform}** at the moment. Please try again later.", parse_mode="Markdown")

def process_otp_check(user_id):
    if user_id in user_states and "page_slug" in user_states[user_id]:
        page_slug = user_states[user_id]["page_slug"]
        site_type = user_states[user_id]["site_type"]
        current_num = user_states[user_id].get("number", "your number")
        
        bot.send_message(user_id, f"⏳ Checking for latest OTP on `{current_num}`...")
        raw_message = fetch_latest_otp(page_slug, site_type)
        otp_code = re.findall(r'\b\d{4,6}\b', raw_message)
        
                if otp_code:
            bot.send_message(user_id, f"💬 **Your OTP Code:** `{otp_code}`\n\n📜 **Full Message:**\n{raw_message}", parse_mode="Markdown")
        else:
            bot.send_message(user_id, f"ℹ️ No specific OTP code found yet. Latest message:\n\n{raw_message}")
    else:
        bot.send_message(user_id, "⚠️ No active session found. Please click **Get Number** first.")

def generate_2fa_otp(message):
    user_id = message.chat.id
    input_text = message.text.strip()
    secret_key = None
    
    try:
        if input_text.startswith("otpauth://"):
            parsed_url = urlparse(input_text)
            query_params = parse_qs(parsed_url.query)
            if 'secret' in query_params:
                secret_key = query_params['secret'].upper()
            else:
                raise ValueError()
        else:
            secret_key = input_text.replace(" ", "").upper()
        
        if secret_key:
            totp = pyotp.TOTP(secret_key)
            current_otp = totp.now()
            time_remaining = totp.interval - (totp.timecode(totp.time_provider.time()) % totp.interval)
            
            bot.send_message(user_id, f"🔐 **Your 2FA OTP Code:** `{current_otp}`\n\n⏳ Valid for another {int(time_remaining)} seconds.", parse_mode="Markdown")
        else:
            raise ValueError()
    except Exception:
        bot.send_message(user_id, "❌ Invalid 2FA Secret Key or Link! Please check and try again.")
    
    user_states[user_id] = {}

# ----------------- MAIN RUN CONTEXT -----------------
if __name__ == '__main__':
    keep_alive()
    print("Bot is starting...")
    bot.infinity_polling()
