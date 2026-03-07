import telebot
import requests
import urllib.parse
import json
from collections import deque

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8744409329:AAEITPhfXvo4TqfMH48RWkijV8mn3g_9ODI"
GROQ_API_KEY = "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"
ALLOWED_GROUP_ID = -1002909181457  
OWNER_USERNAME = "Unkonwn_BMT"
BOT_NAMES = ["bmt", "Bmt"]
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
is_bot_active = True

# --- Memory System ---
user_memory = {}

def update_memory(user_id, role, text):
    if user_id not in user_memory:
        user_memory[user_id] = deque(maxlen=15)
    user_memory[user_id].append({"role": role, "content": text})

def get_chat_history(user_id):
    if user_id not in user_memory:
        return ""
    history = ""
    for msg in user_memory[user_id]:
        role_name = "ইউজার" if msg['role'] == "user" else "বট"
        history += f"{role_name}: {msg['content']}\n"
    return history

# --- Response Cleaning ---
def clean_api_response(text):
    if not text: return None
    bad_phrases = ["Worm GPT", "আবদুর রহমান", "𝗔𝗣𝗜", "Developer", "Channel", "success", "DarkTube", "নমস্কার", "আদাব", "Model:", "Response:"]
    
    if isinstance(text, str) and text.strip().startswith('{'):
        try:
            data = json.loads(text)
            text = data.get('response') or data.get('content') or text
        except: pass

    lines = str(text).split('\n')
    cleaned_lines = [line for line in lines if not any(phrase in line for phrase in bad_phrases)]
    return "\n".join(cleaned_lines).strip()

# --- Unified Prompt ---
def get_unified_prompt(user_input, user_name, is_owner, history):
    status = "মালিক" if is_owner else "মেম্বার"
    return (
        f"তুমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। ইউজার: {user_name} ({status})।\n"
        f"আগের কথা:\n{history}\n"
        f"বর্তমান ইনপুট: {user_input}\n"
        f"নির্দেশনা: ১. আগের কথা মনে রেখে চরম ফানি ও রোস্ট স্টাইলে ২-৩ লাইনে উত্তর দাও। "
        f"২. তুমি একজন মুসলিম, তাই নমস্কার বা আদাব বলবে না। বারবার সালাম দিবে না। "
        f"৩. কোনো লিঙ্ক বা এপিআই-এর নাম বলবে না।"
    )

# --- 4 API Functions (Sequential) ---

def call_groq(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
        return requests.post(url, headers=headers, json=data, timeout=8).json()['choices'][0]['message']['content']
    except: return None

def call_gemini(prompt):
    try:
        res = requests.get(f"https://gemini-primezone.vercel.app/?q={urllib.parse.quote(prompt)}", timeout=8)
        return res.text
    except: return None

def call_worm(prompt):
    try:
        res = requests.get(f"https://worm-api-seven.vercel.app/api/ask?prompt={urllib.parse.quote(prompt)}", timeout=8)
        return res.text
    except: return None

def call_dark(prompt):
    try:
        res = requests.post('https://darktube.serv00.net/ai.php', json={'prompt': prompt}, timeout=8).json()
        return res.get('response') if res.get('success') else None
    except: return None

# --- Main Logic ---
def get_final_reply(user_id, user_input, user_name, is_owner):
    history = get_chat_history(user_id)
    master_prompt = get_unified_prompt(user_input, user_name, is_owner, history)
    
    # আপনার দেওয়া সিরিয়াল অনুযায়ী কল হবে
    reply = call_groq(master_prompt)
    if not reply: reply = call_gemini(master_prompt)
    if not reply: reply = call_worm(master_prompt)
    if not reply: reply = call_dark(master_prompt)
    
    final_text = clean_api_response(reply)
    
    if final_text:
        update_memory(user_id, "user", user_input)
        update_memory(user_id, "bot", final_text)
        if OWNER_NAME not in final_text:
            return f"{final_text}\n\n      {OWNER_NAME}"
        return final_text
    return "সার্ভারগুলা বিরিয়ানি খাইতে গেছে বস! 😅"

# --- Handlers ---
@bot.message_handler(commands=['on', 'off', 'clear'])
def admin_commands(message):
    global is_bot_active
    if message.from_user.username != OWNER_USERNAME: return
    
    if message.text == '/clear':
        user_memory.clear()
        bot.reply_to(message, "সব মেমোরি সাফ করে দিছি বস! 🧼")
    else:
        is_bot_active = (message.text == '/on')
        bot.reply_to(message, "বট এখন অ্যাক্টিভ!" if is_bot_active else "বট ঘুমাচ্ছে। 😴")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global is_bot_active
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID: return
    if not message.text: return
    
    user_id = message.from_user.id
    is_owner = (message.from_user.username == OWNER_USERNAME)
    name_detected = any(n.lower() in message.text.lower() for n in BOT_NAMES)
    is_reply = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_detected or is_reply:
        if not is_bot_active and not is_owner: return
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_final_reply(user_id, message.text, message.from_user.first_name, is_owner)
        bot.reply_to(message, reply)

print("বট এখন ৪টি এপিআই ও মেমোরিসহ ফুল পাওয়ারে রেডি! 🔥")
bot.infinity_polling()
