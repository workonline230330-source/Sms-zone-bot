import os
import pyotp
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

keep_alive()


# ==========================================
# ২. টেলিগ্রাম বটের মূল কনফিগারেশন ও বাটন সেটআপ
# ==========================================
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ব্যবহারকারী এখন 2FA ইনপুট দেওয়ার অবস্থায় আছে কিনা তা ট্র্যাক করার জন্য
user_states = {}

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states[message.chat.id] = None # স্টেট রিসেট
    welcome_text = "Social media SMS zone bot-এ আপনাকে স্বাগতম!\nনিচের বাটনগুলো ব্যবহার করুন:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())


@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    user_id = message.chat.id
    user_text = message.text

    # ব্যবহারকারী যদি 2FA কি (Key) দেওয়ার অবস্থায় থাকে
    if user_states.get(user_id) == "WAITING_FOR_2FA":
        secret_key = user_text.replace(" ", "").strip()
        
        try:
            totp = pyotp.TOTP(secret_key)
            live_code = totp.now()
            
            response = (
                "✅ **SUCCESSFUL GENERATED**\n\n"
                f"🔑 YOUR 2FA CODE: `{live_code}`\n\n"
                "⏱️ এই কোডটি পরবর্তী ৩০ সেকেন্ডের জন্য কার্যকর থাকবে। কোডটি কপি করতে সেটির ওপর ট্যাপ করুন।"
            )
            bot.send_message(user_id, response, parse_mode="Markdown", reply_markup=main_menu())
            user_states[user_id] = None # কাজ শেষ, স্টেট রিসেট
            
        except Exception as e:
            bot.send_message(user_id, "❌ আপনার দেওয়া 2FA Secret Key টি সঠিক নয়। অনুগ্রহ করে সঠিক কি (Key) পুনরায় পাঠান অথবা Cancel করুন।")
        return

    # প্রতিটি মেসেজের শেষে আপনার কথা মতো "ইনশাআল্লাহ।" যোগ করা হলো
    if "GET NUMBER" in user_text:
        bot.send_message(user_id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    elif "SUPPORT" in user_text:
        response_text = "যেকোনো সমস্যায় সরাসরি আমাদের অ্যাডমিনের সাথে যোগাযোগ করুন: @Shar_iyar"
        bot.send_message(user_id, response_text)

    elif "Search Number" in user_text:
        bot.send_message(user_id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    elif "TRAFFIC" in user_text:
        bot.send_message(user_id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    # 2FA ONLINE বাটন
    elif "2FA ONLINE" in user_text:
        user_states[user_id] = "WAITING_FOR_2FA"
        
        inline_markup = InlineKeyboardMarkup()
        cancel_button = InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel_action")
        inline_markup.add(cancel_button)
        
        response_text = (
            "《 🔹 ENTER 2FA KEY 》\n\n"
            "🔹 SEND YOUR 2FA SECRET KEY"
        )
        bot.send_message(user_id, response_text, reply_markup=inline_markup)

    elif "Refer" in user_text:
        bot.send_message(user_id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ।")

    elif "WITHDRAWAL" in user_text:
        bot.send_message(user_id, "আমাদের কাজ চলতেছে খুব শীঘ্রই চালু হবে ইনশাআল্লাহ。")

    else:
        bot.send_message(user_id, "অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন!", reply_markup=main_menu())


# Cancel বাটনে চাপ দিলে যা হবে
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.message.chat.id
    if call.data == "cancel_action":
        user_states[user_id] = None
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "অ্যাকশন বাতিল করা হয়েছে।", reply_markup=main_menu())


# বট রানিং করার ফাইনাল কোড
print("Bot is starting successfully...")
bot.infinity_polling()
