import telebot
import requests
import urllib.parse
import json

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8744409329:AAEITPhfXvo4TqfMH48RWkijV8mn3g_9ODI"
GROQ_API_KEY = "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"
ALLOWED_GROUP_ID = -1002909181457  

BOT_NAMES = ["bmt", "Bmt", "BMT"]  
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"
OWNER_USERNAME = "Unkonwn_BMT"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- Response Cleaning Function ---
def clean_api_response(text):
    if not text: return None
    
    # এই লিস্টে ওইসব শব্দ দিন যা আপনি রিমুভ করতে চান
    garbage_list = [
        "𝗔𝗣𝗜 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", "𝗔𝗣𝗜 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿", "Offline_669", "VPSTECH_BD", 
        "Developer", "Channel", "@", "http", "https", "model", "response"
    ]
    
    # যদি JSON ফরম্যাটে ডাটা আসে তবে শুধু মেইন টেক্সটটা নিবে
    if text.startswith('{') and 'response' in text:
        try:
            data = json.loads(text)
            text = data.get('response', text)
        except: pass

    # বাড়তি লাইনগুলো ডিলিট করার লজিক
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # যদি লাইনের ভেতর গারবেজ শব্দগুলো না থাকে তবেই সেটা নিবে
        if not any(garbage in line for garbage in garbage_list):
            cleaned_lines.append(line)
    
    return "\n".join(cleaned_lines).strip()

def get_master_prompt(user_input, user_name, is_owner):
    owner_context = "মালিকের (বস) সাথে কথা বলছো।" if is_owner else "ইউজারের সাথে কথা বলছো।"
    return (
        f"তোমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। {owner_context} "
        f"নির্দেশনা: ১. খুব সংক্ষেপে এবং মজার ছলে উত্তর দাও। "
        f"২. মেম্বারদের হালকা পচাও কিন্তু বকবক করবে না। ২-৩ লাইনে শেষ করো। "
        f"৩. প্রতিটি উত্তরের শেষে ৫টি স্পেস দিয়ে '{OWNER_NAME}' লিখবে। "
        f"৪. ইনপুট: {user_input}"
    )

# --- API Functions ---
def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10)
        return res.json()['choices'][0]['message']['content']
    except: return None

def call_gemini_prime(prompt):
    try:
        url = f"https://gemini-primezone.vercel.app/?q={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=10)
        return res.text
    except: return None

def call_worm_api(prompt):
    try:
        url = f"https://worm-api-seven.vercel.app/api/ask?prompt={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=10)
        return res.text
    except: return None

# --- Hybrid Logic ---
def get_final_reply(user_input, user_name, is_owner):
    prompt = get_master_prompt(user_input, user_name, is_owner)
    
    # সিরিয়াল ট্রাই
    reply = call_groq(prompt)
    if not reply: reply = call_gemini_prime(prompt)
    if not reply: reply = call_worm_api(prompt)
    
    # ক্লিন করা
    final_text = clean_api_response(reply)
    
    if final_text:
        # সিগনেচার চেক
        if OWNER_NAME not in final_text:
            final_text = f"{final_text}\n\n      {OWNER_NAME}"
        return final_text
    return "সার্ভার একটু বিজি বস! 😅"

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID:
        return 
    if not message.text: return
    
    is_owner = (message.from_user.username == OWNER_USERNAME)
    name_detected = any(name.lower() in message.text.lower() for name in BOT_NAMES)
    is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_detected or is_reply_to_bot:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_final_reply(message.text, message.from_user.first_name, is_owner)
        bot.reply_to(message, reply)

bot.infinity_polling()
