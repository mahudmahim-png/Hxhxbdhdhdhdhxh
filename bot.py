import telebot
import requests

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8626861144:AAGBFKDBubylAXt2tNpm9iru2pm-P4La4aI"
GROQ_API_KEY = "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"

BOT_NAMES = ["bmt", "Bmt", "BMT"]  
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"
OWNER_NW = "@Unkonwn_BMT"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Welcome Message (Sudhu notun member join korle salam dibe)
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        welcome_text = f"আসসালামু আলাইকুম {member.first_name}!\nআমাদের গ্রুপে আপনাকে স্বাগতম।\n\n{OWNER_NAME}"
        bot.send_message(message.chat.id, welcome_text)

def get_groq_response(user_input, user_name):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # SYSTEM PROMPT: Ekhane 'Always salam' bad dewa hoyeche
    system_prompt = f"""
    তুমার নাম {BOT_NAMES[0]}। তুমাকে তৈরি করেছে {OWNER_NAME}। তোমার মালিক হলো {OWNER_NW}।
    ১. শুধুমাত্র শুদ্ধ বাংলা ভাষায় কথা বলবে। কোনো ইংরেজি বা বাংলিশ ব্যবহার করবে না।
    ২. কথা বলার সময় খুব মজার, চটপটে এবং স্বাভাবিক (Natural) হবে। 
    ৩. প্রতি কথায় সালাম দেওয়ার দরকার নেই। কেউ সালাম দিলে বা নতুন কথা শুরু করলে শুধু তখন সালাম দিবে।
    ৪. একজন ভদ্র মুসলমানের মতো আচরণ করবে কিন্তু রোবটের মতো বার বার একই কথা বলবে না।
    ৫. প্রতিটি উত্তরের শেষে অবশ্যই "{OWNER_NAME}" এই লেখাটি ৫-৬ টি স্পেস দিয়ে যুক্ত করবে।
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User {user_name} says: {user_input}"}
        ],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "মাথাটা একটু ঘুরছে রে ভাই!"
    except:
        return "নেটওয়ার্কের সমস্যা!"

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if not message.text: return
    
    user_text = message.text
    user_name = message.from_user.first_name
    
    name_detected = any(name in user_text for name in BOT_NAMES)
    should_respond = False
    
    if message.chat.type == "private":
        should_respond = True
    else:
        if name_detected or (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id):
            should_respond = True

    if should_respond:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_groq_response(user_text, user_name)
        bot.reply_to(message, reply)

print(f"বট এখন আরও ন্যাচারাল ভাবে কথা বলবে!")
bot.infinity_polling()
