import telebot
import requests
import urllib.parse

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8744409329:AAEITPhfXvo4TqfMH48RWkijV8mn3g_9ODI"
GROQ_API_KEY = "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"
ALLOWED_GROUP_ID = -1002909181457  

BOT_NAMES = ["bmt", "Bmt", "BMT"]  
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"
OWNER_USERNAME = "Unkonwn_BMT"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- Common Master Prompt ---
def get_master_prompt(user_input, user_name, is_owner):
    owner_context = "তুমি এখন তোমার মালিকের (বস) সাথে কথা বলছো।" if is_owner else "তুমি ইউজারের সাথে কথা বলছো।"
    return (
        f"তোমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। মালিক {OWNER_USERNAME}। "
        f"ইউজার নাম: {user_name}। {owner_context} "
        f"নির্দেশনা: ১. শুধুমাত্র শুদ্ধ বাংলা ও চরম মজার ভাষায় কথা বলো। "
        f"২. মেম্বারদের সাথে ফাজলামি করো এবং কেউ পচাতে চাইলে তাকে রোস্ট করে দাও। "
        f"৩. প্রতিটি উত্তরের শেষে অবশ্যই ৫-৬টি স্পেস দিয়ে '{OWNER_NAME}' লিখবে। "
        f"৪. ইউজার ইনপুট: {user_input}"
        f"৫. তোমার কাজ সবাইকে হাসানো "
    )

# --- API Functions ---

def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=8)
        return res.json()['choices'][0]['message']['content']
    except: return None

def call_tech_master(prompt):
    try:
        url = f"https://www.gajarbotol.site/Tech_master/api/custom-ai.php?prompt={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=8)
        return res.text.strip()
    except: return None

def call_gemini_prime(prompt):
    try:
        url = f"https://gemini-primezone.vercel.app/?q={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=8)
        return res.text.strip()
    except: return None

def call_worm_api(prompt):
    try:
        url = f"https://worm-api-seven.vercel.app/api/ask?prompt={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=8)
        return res.json().get('response') or res.json().get('content')
    except: return None

def call_quill_bot(prompt):
    try:
        url = f"https://quill-bot-prime.vercel.app/quillbot?q={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=8)
        return res.text.strip()
    except: return None

# --- Hybrid Logic (Failover) ---
def get_final_reply(user_input, user_name, is_owner):
    prompt = get_master_prompt(user_input, user_name, is_owner)
    
    # সিরিয়াল অনুযায়ী ট্রাই করবে
    reply = call_groq(prompt)
    if not reply: reply = call_tech_master(prompt)
    if not reply: reply = call_gemini_prime(prompt)
    if not reply: reply = call_worm_api(prompt)
    if not reply: reply = call_quill_bot(prompt)
    
    if reply:
        if OWNER_NAME not in reply:
            reply = f"{reply}\n\n      {OWNER_NAME}"
        return reply
    return "বস, সবগুলা সার্ভার একলগে জ্যাম হয়ে গেছে! টিম বিএমটি-কে জানান। 😅"

# --- Message Handlers ---

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    if message.chat.id == ALLOWED_GROUP_ID:
        for member in message.new_chat_members:
            bot.reply_to(message, f"আসসালামু আলাইকুম {member.first_name}! টিম বিএমটি-র গ্রুপে স্বাগতম। 😊\n\n{OWNER_NAME}")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID:
        return 

    if not message.text: return
    
    user_text = message.text
    user_name = message.from_user.first_name
    is_owner = (message.from_user.username == OWNER_USERNAME)
    
    name_detected = any(name.lower() in user_text.lower() for name in BOT_NAMES)
    is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_detected or is_reply_to_bot:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_final_reply(user_text, user_name, is_owner)
        bot.reply_to(message, reply)

print(f"৫টি এপিআই দিয়ে হাইব্রিড বট এখন অন ফায়ার! 🔥")
bot.infinity_polling()
