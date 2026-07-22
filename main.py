import os
from flask import Flask
from threading import Thread
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ১. Render Free Tier-এর জন্য ডামি ওয়েব সার্ভার
# ==========================================
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

# ওয়েব সার্ভার ব্যাকগ্রাউন্ডে চালু করা
keep_alive()


# ==========================================
# ২. টেলিগ্রাম বটের মূল কনফিগারেশন ও বাটন সেটআপ
# ==========================================
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# মূল কিবোর্ড মেনু তৈরি
def main_menu():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    btn1 = KeyboardButton("📲 GET NUMBER")
    btn2 = KeyboardButton("🔍 Search Number")
    btn3 = KeyboardButton("📊 TRAFFIC")
    btn4 = KeyboardButton("🔒 2FA ONLINE")
    btn5 = KeyboardButton("🎁 Refer")
    btn6 = KeyboardButton("💳 WITHDRAWAL")
    btn7 = KeyboardButton("👤 SUPPORT")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    return markup


# ==========================================
# ৩. বটের মেসেজ ও কমান্ড হ্যান্ডলারসমূহ
# ==========================================

# /start কমান্ড দিলে যে রেসপন্স করবে
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Social media SMS zone bot-এ আপনাকে স্বাগতম!\nনিচের বাটনগুলো ব্যবহার করুন:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())


# বাটনগুলোর ওপর ক্লিক করলে যা কাজ করবে
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_text = message.text

    # GET NUMBER বাটন
    if "GET NUMBER" in user_text:
        bot.send_message(message.chat.id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    # SUPPORT বাটন
    elif "SUPPORT" in user_text:
        support_markup = InlineKeyboardMarkup()
        contact_button = InlineKeyboardButton(text="💬 Contact Admin Directly", url="https://t.me")
        support_markup.add(contact_button)
        bot.send_message(message.chat.id, "যেকোনো সমস্যায় সরাসরি আমাদের অ্যাডমিনের সাথে যোগাযোগ করুন 📬।", reply_markup=support_markup)

    # Search Number বাটন
    elif "Search Number" in user_text:
        bot.send_message(message.chat.id, "নাম্বার সার্চ করার অপশনটি খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    # TRAFFIC বাটন
    elif "TRAFFIC" in user_text:
        bot.send_message(message.chat.id, "বর্তমান কোনো সার্ভার যোগাযোগ করা নায়🥺 আমরা খুব শিঘ্রই চালু করব ইনশাআল্লাহ।")

    # 2FA ONLINE বাটন
    elif "2FA ONLINE" in user_text:
        inline_markup = InlineKeyboardMarkup()
        url_button = InlineKeyboardButton(text="🔗 Open 2FA Live Website", url="https://co.com")
        inline_markup.add(url_button)
        response_text = "🔒 **2FA ONLINE CODE GENERATOR**\n\nআপনার টু-ফ্যাক্টর সিক্রেট কি (Secret Key) থেকে লাইভ ৬ সংখ্যার ওটিপি কোড বের করতে নিচের বোতামে ক্লিক করুন।"
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown", reply_markup=inline_markup)

    # Refer বাটন (নতুন মেসেজ যোগ করা হয়েছে)
    elif "Refer" in user_text:
        bot.send_message(message.chat.id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ")

    # WITHDRAWAL বাটন (নতুন মেসেজ যোগ করা হয়েছে)
    elif "WITHDRAWAL" in user_text:
        bot.send_message(message.chat.id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    else:
        bot.send_message(message.chat.id, "অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন!", reply_markup=main_menu())


# বট রানিং করার ফাইনাল কোড
print("Bot is starting successfully...")
bot.infinity_polling()
