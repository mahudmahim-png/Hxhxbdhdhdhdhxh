import telebot
import requests
import urllib.parse
import json

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8744409329:AAEITPhfXvo4TqfMH48RWkijV8mn3g_9ODI"
GROQ_API_KEY = "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"
ALLOWED_GROUP_ID = -1002909181457  
OWNER_USERNAME = "Unkonwn_BMT"
BOT_NAMES = ["bmt", "Bmt"]
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
is_bot_active = True
all_users = set() # ব্রডকাস্টিং এর জন্য

# --- Response Cleaning ---
def clean_api_response(text):
    if not text: return None
    bad_phrases = ["Worm GPT", "আবদুর রহমান", "𝗔𝗣𝗜", "Developer", "Channel", "success", "DarkTube", "নমস্কার", "আদাব", "Model:", "Response:", "ইনপুট:", "প্রম্পট:"]
    
    if isinstance(text, str) and text.strip().startswith('{'):
        try:
            data = json.loads(text)
            text = data.get('response') or data.get('content') or text
        except: pass

    lines = str(text).split('\n')
    cleaned_lines = [line for line in lines if not any(phrase in line.lower() for phrase in [b.lower() for b in bad_phrases])]
    return "\n".join(cleaned_lines).strip()

# --- Unified Prompt (No Memory) ---
def get_unified_prompt(user_input, user_name, is_owner):
    status = "বস" if is_owner else "মেম্বার"
    return (
        f"তুমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। ইউজার: {user_name} ({status})। "
        f"নির্দেশনা: ১. চরম ফানি ও রোস্ট মাস্টার স্টাইলে ২ লাইনে উত্তর দাও। "
        f"২. তুমি একজন মুসলিম, তাই নমস্কার বা আদাব বলবে না। ৩. কোনো এপিআই-এর নাম বলবে না। "
        f"৪. ইনপুট: {user_input}"
    )

# --- API Functions ---
def call_api_sequential(prompt):
    # 1. Groq
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        if res.status_code == 200: return res.json()['choices'][0]['message']['content']
    except: pass

    # 2. Gemini
    try:
        res = requests.get(f"https://gemini-primezone.vercel.app/?q={urllib.parse.quote(prompt)}", timeout=10)
        if res.status_code == 200: return res.text
    except: pass

    # 3. Worm
    try:
        res = requests.get(f"https://worm-api-seven.vercel.app/api/ask?prompt={urllib.parse.quote(prompt)}", timeout=10)
        if res.status_code == 200: return res.text
    except: pass

    # 4. DarkTube
    try:
        res = requests.post('https://darktube.serv00.net/ai.php', json={'prompt': prompt}, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('success'): return data.get('response')
    except: pass

    return None

# --- Admin Handlers ---
@bot.message_handler(commands=['on', 'off', 'broadcast'])
def admin_commands(message):
    global is_bot_active
    if message.from_user.username != OWNER_USERNAME: return
    
    cmd = message.text.split()[0]
    
    if cmd == '/on':
        is_bot_active = True
        bot.reply_to(message, "বট সজাগ! 🔥")
    elif cmd == '/off':
        is_bot_active = False
        bot.reply_to(message, "বট ঘুমে। 😴")
    elif cmd == '/broadcast':
        msg_to_send = message.text.replace('/broadcast', '').strip()
        if not msg_to_send:
            bot.reply_to(message, "মেসেজ দিন। উদা: /broadcast হাই")
            return
        count = 0
        for uid in all_users:
            try:
                bot.send_message(uid, f"📢 **নোটিশ:**\n\n{msg_to_send}\n\n{OWNER_NAME}")
                count += 1
            except: pass
        bot.reply_to(message, f"{count} জনকে পাঠানো হয়েছে।")

# --- Main Handler ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global is_bot_active
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID: return
    if not message.text: return
    
    user_id = message.from_user.id
    all_users.add(user_id) # ব্রডকাস্টিং লিস্ট আপডেট
    
    is_owner = (message.from_user.username == OWNER_USERNAME)
    name_detected = any(n.lower() in message.text.lower() for n in BOT_NAMES)
    is_reply = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_detected or is_reply:
        if not is_bot_active and not is_owner: return
        bot.send_chat_action(message.chat.id, 'typing')
        
        prompt = get_unified_prompt(message.text, message.from_user.first_name, is_owner)
        reply = call_api_sequential(prompt)
        final_text = clean_api_response(reply)
        
        if final_text:
            bot.reply_to(message, f"{final_text}\n\n      {OWNER_NAME}")
        else:
            bot.reply_to(message, "সার্ভার জ্যাম বস! 😅")

print("বট এখন মেমোরি ছাড়া সুপার ফাস্ট স্পিডে রেডি! 🔥")
bot.infinity_polling()
