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

# বট স্ট্যাটাস (ডিফল্ট অন)
is_bot_active = True

# --- Response Cleaning Function ---
def clean_api_response(text):
    if not text: return None
    garbage_list = ["𝗔𝗣𝗜 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", "𝗔𝗣𝗜 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿", "Offline_669", "VPSTECH_BD", "success", "DarkTube"]
    
    if isinstance(text, str) and text.strip().startswith('{'):
        try:
            data = json.loads(text)
            text = data.get('response', text)
        except: pass

    lines = str(text).split('\n')
    cleaned_lines = [line for line in lines if not any(g in line for g in garbage_list)]
    return "\n".join(cleaned_lines).strip()

def get_master_prompt(user_input, user_name, is_owner):
    status = "বস" if is_owner else "ইউজার"
    return (f"তুমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। তুমি {user_name} ({status})-এর সাথে কথা বলছো। "
            f"নির্দেশনা: ১. শুদ্ধ বাংলা ও মজার ভাষায় ছোট উত্তর দাও। ২. ২-৩ লাইনে শেষ করো। "
            f"৩. শেষে ৫টি স্পেস দিয়ে '{OWNER_NAME}' লিখবে। ৪. ইনপুট: {user_input}")

# --- API Functions ---
def call_groq(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
        res = requests.post(url, headers=headers, json=data, timeout=8)
        return res.json()['choices'][0]['message']['content']
    except: return None

def call_gemini_prime(prompt):
    try:
        url = f"https://gemini-primezone.vercel.app/?q={urllib.parse.quote(prompt)}"
        return requests.get(url, timeout=8).text
    except: return None

def call_worm_api(prompt):
    try:
        url = f"https://worm-api-seven.vercel.app/api/ask?prompt={urllib.parse.quote(prompt)}"
        return requests.get(url, timeout=8).text
    except: return None

def call_darktube(prompt):
    try:
        url = 'https://darktube.serv00.net/ai.php'
        res = requests.post(url, json={'prompt': prompt}, timeout=8)
        data = res.json()
        return data.get('response') if data.get('success') else None
    except: return None

def get_final_reply(user_input, user_name, is_owner):
    prompt = get_master_prompt(user_input, user_name, is_owner)
    reply = call_groq(prompt) or call_gemini_prime(prompt) or call_worm_api(prompt) or call_darktube(prompt)
    final_text = clean_api_response(reply)
    if final_text:
        return f"{final_text}\n\n      {OWNER_NAME}" if OWNER_NAME not in final_text else final_text
    return "বস, সব সার্ভার জ্যাম! 😅"

# --- Admin Commands ---
@bot.message_handler(commands=['on', 'off'])
def toggle_bot(message):
    global is_bot_active
    if message.from_user.username != OWNER_USERNAME:
        bot.reply_to(message, "এই পাওয়ার শুধু আমার বসের কাছে আছে! আপনি দূরে গিয়া খেলেন। 🐸")
        return

    if message.text == '/on':
        is_bot_active = True
        bot.reply_to(message, "আমি আবার ফিরে এসেছি বস! এখন সবাই আমাকে ডাকতে পারে। 😎")
    elif message.text == '/off':
        is_bot_active = False
        bot.reply_to(message, "বট এখন বিশ্রামে গেল। আপনি ছাড়া কেউ আমাকে আর পাবে না। 😴")

# --- Main Message Handler ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global is_bot_active
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID:
        return 
    if not message.text: return
    
    is_owner = (message.from_user.username == OWNER_USERNAME)
    name_detected = any(name.lower() in message.text.lower() for name in BOT_NAMES)
    is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_detected or is_reply_to_bot:
        if not is_bot_active and not is_owner:
            bot.reply_to(message, "বস আমাকে এখন ঘুমাতে বলছে, পরে কথা হবে! 💤")
            return
            
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_final_reply(message.text, message.from_user.first_name, is_owner)
        bot.reply_to(message, reply)

print(f"বট এখন অ্যাডমিন কন্ট্রোলসহ রেডি! 🔥")
bot.infinity_polling()
