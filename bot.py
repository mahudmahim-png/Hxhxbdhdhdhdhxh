import telebot
import requests
import urllib.parse
import json

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8744409329:AAEITPhfXvo4TqfMH48RWkijV8mn3g_9ODI"
GROQ_API_KEY = "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"
ALLOWED_GROUP_ID = -1002909181457  
OWNER_USERNAME = "Unkonwn_BMT" # এখানে @ ছাড়া দিবেন যাতে কমান্ড কাজ করে
BOT_NAMES = ["bmt", "Bmt"]
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
is_bot_active = True
last_api_used = "None" 
all_users = set()

# --- Response Cleaning & Pretty Output ---
def clean_api_response(text):
    if not text: return None
    
    # এপিআই যদি JSON পাঠায়, তবে তা থেকে আসল মেসেজ বের করা (Pretty Print Logic)
    if isinstance(text, str) and (text.strip().startswith('{') or text.strip().startswith('[')):
        try:
            data = json.loads(text)
            # সিরিয়াল অনুযায়ী সম্ভাব্য Key চেক করা
            text = data.get('result') or data.get('response') or data.get('content') or data.get('message') or text
        except: pass

    # ফালতু লেখা রিমুভ করা
    bad_phrases = ["Worm GPT", "tech master", "@abdur081", "আবদুর রহমান", "𝗔𝗣𝗜", "Developer", "success", "DarkTube", "Model:", "Response:"]
    
    if not isinstance(text, str): text = str(text)
    
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not any(phrase.lower() in line.lower() for phrase in bad_phrases)]
    return "\n".join(cleaned_lines).strip()

# --- Unified Prompt ---
def get_unified_prompt(user_input, user_name, is_owner):
    status = "মালিক" if is_owner else "মেম্বার"
    return (
        f"তুমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। তেমাকে তৈরি করেছেন যিনি তার ইউজার নাম @{OWNER_USERNAME}। "
        f"ইউজার: {user_name} ({status})। "
        f"নির্দেশনা: ১. শুদ্ধ বাংলায় এবং চরম ফানি রোস্ট স্টাইলে ২ থেকে ৩ লাইনে উত্তর দাও, বেশী বড় আবার বেশী ছোটও না কিন্তু মজার। ২. বাংলিশ বলবে না, ইমোজি ব্যবহার করবে। "
        f"৩. এপিআই এর নাম বলবে না। ইনপুট: {user_input}"
    )

# --- Sequential API System (৬টি এপিআই) ---
def call_api_sequential(prompt):
    global last_api_used
    encoded_prompt = urllib.parse.quote(prompt)
    
    # ১. Gemini Prime (Existing)
    try:
        res = requests.get(f"https://gemini-primezone.vercel.app/?q={encoded_prompt}", timeout=10)
        if res.status_code == 200:
            last_api_used = "Gemini Prime"
            return res.text
    except: pass

    # ২. Gajarbotol (New API - Tech Master)
    try:
        res = requests.get(f"https://www.gajarbotol.site/Tech_master/api/custom-ai.php?prompt={encoded_prompt}", timeout=10)
        if res.status_code == 200:
            last_api_used = "Tech Master"
            return res.text
    except: pass

    # ৩. Gemini Vercel (New API - Abdur)
    try:
        res = requests.get(f"https://gemini-api-bay-ten.vercel.app/api/ask?prompt={encoded_prompt}", timeout=10)
        if res.status_code == 200:
            last_api_used = "Gemini Vercel"
            return res.text
    except: pass

    # ৪. Worm GPT
    try:
        res = requests.get(f"https://worm-api-seven.vercel.app/api/ask?prompt={encoded_prompt}", timeout=10)
        if res.status_code == 200:
            last_api_used = "Worm GPT"
            return res.text
    except: pass

    # ৫. DarkTube
    try:
        res = requests.post('https://darktube.serv00.net/ai.php', json={'prompt': prompt}, timeout=10)
        if res.status_code == 200:
            last_api_used = "DarkTube"
            return res.json().get('response')
    except: pass

    # ৬. Groq (সবার শেষে)
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8}
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=12)
        if res.status_code == 200:
            last_api_used = "Groq"
            return res.json()['choices'][0]['message']['content']
    except: pass

    last_api_used = "All APIs Failed"
    return None

# --- Admin Commands ---
@bot.message_handler(commands=['on', 'off', 'api', 'broadcast'])
def admin_commands(message):
    global is_bot_active, last_api_used
    if message.from_user.username != OWNER_USERNAME: return
    
    cmd = message.text.split()[0]
    if cmd == '/on':
        is_bot_active = True
        bot.reply_to(message, "বট এখন অ্যাক্টিভ! 🔥")
    elif cmd == '/off':
        is_bot_active = False
        bot.reply_to(message, "বট এখন বিশ্রামে। 😴")
    elif cmd == '/api':
        bot.reply_to(message, f"📊 **API Status:**\nসর্বশেষ সফল রিকোয়েস্ট: `{last_api_used}`")
    elif cmd == '/broadcast':
        msg_to_send = message.text.replace('/broadcast', '').strip()
        if not msg_to_send: return
        count = 0
        for uid in list(all_users):
            try:
                bot.send_message(uid, f"📢 **নোটিশ:**\n\n{msg_to_send}\n\n{OWNER_NAME}")
                count += 1
            except: pass
        bot.reply_to(message, f"সাফল্যের সাথে {count} জনকে জানানো হয়েছে।")

# --- Main Message Handler ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global is_bot_active
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID: return
    if not message.text: return
    
    user_id = message.from_user.id
    all_users.add(user_id)
    
    is_owner = (message.from_user.username == OWNER_USERNAME)
    name_detected = any(n.lower() in message.text.lower() for n in BOT_NAMES)
    is_reply = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_detected or is_reply:
        if not is_bot_active and not is_owner:
            bot.reply_to(message, "বস আমাকে এখন ঘুমাতে বলছে। পরে আসিস! 💤")
            return
            
        bot.send_chat_action(message.chat.id, 'typing')
        prompt = get_unified_prompt(message.text, message.from_user.first_name, is_owner)
        reply = call_api_sequential(prompt)
        final_text = clean_api_response(reply)
        
        if final_text:
            bot.reply_to(message, f"{final_text}\n\n      {OWNER_NAME}")
        else:
            bot.reply_to(message, "সার্ভারগুলা বিরিয়ানি খাইতে গেছে বস! 😅")

print("৬টি এপিআই সহ বট একদম ক্লিনভাবে রেডি! 🔥")
bot.infinity_polling()
