import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# টোকেনটি রেন্ডার এনভায়রনমেন্ট থেকে আসবে
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    
    btn1 = KeyboardButton("📲 GET NUMBER")
    btn2 = KeyboardButton("🔍 Search Number")
    btn3 = KeyboardButton("📊 TRAFFIC")
    btn4 = KeyboardButton("🔓 2FA ONLINE")
    btn5 = KeyboardButton("🎁 Refer")
    btn6 = KeyboardButton("💳 WITHDRAWAL")
    btn7 = KeyboardButton("👤 SUPPORT")
    
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7)
    
    welcome_text = "Welcome to **Social media SMS zone** bot! 🤖\n\nআমাদের কাস্টম এসএমএস জোন প্যানেল চালু হয়েছে। নিচের বাটনগুলো ব্যবহার করুন:"
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if "GET NUMBER" in message.text:
        bot.reply_to(message, "টেলিগ্রাম বা অন্যান্য সার্ভিসের নাম্বার নেওয়ার মেনু এখানে আসবে।")
    elif "Search Number" in message.text:
        bot.reply_to(message, "নাম্বার সার্চ করার অপশন।")
    elif "TRAFFIC" in message.text:
        bot.reply_to(message, "বটের ট্রাফিক এবং স্ট্যাটিস্টিকস।")
    elif "2FA ONLINE" in message.text:
        bot.reply_to(message, "২-স্টেপ ভেরিফিকেশন (2FA) অনলাইন প্যানেল।")
    elif "Refer" in message.text:
        bot.reply_to(message, "আপনার রেফারেল লিংক এবং বোনাস ডিটেইলস।")
    elif "WITHDRAWAL" in message.text:
        bot.reply_to(message, "টাকা বা ব্যালেন্স উইথড্র করার মেনু।")
    elif "SUPPORT" in message.text:
        bot.reply_to(message, "যেকোনো সমস্যায় অ্যাডমিনের সাথে যোগাযোগ করুন।")

if __name__ == "__main__":
    print("Social media SMS zone বটটি সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
