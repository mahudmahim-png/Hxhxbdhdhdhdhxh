import telebot
import requests
import urllib.parse
import json
import time
from telebot import types
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8744409329:AAEITPhfXvo4TqfMH48RWkijV8mn3g_9ODI"
GROQ_API_KEY = "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"
ALLOWED_GROUP_ID = -1002909181457  
OWNER_USERNAME = "Unkonwn_BMT"
BOT_NAMES = ["bmt", "Bmt"]
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
start_time = time.time()

# --- বিস্তারিত স্ট্যাটাস ট্র্যাকার ---
stats = {
    "total_requests": 0,
    "groq_hits": 0,
    "gemini_hits": 0,
    "worm_hits": 0,
    "darktube_hits": 0,
    "failed_hits": 0,
    "is_bot_active": True,
    "last_api": "None"
}

# ইউজার ডাটাবেজ (In-memory)
all_users = set()

# --- ইউটিলিটি ফাংশন (সার্ভার হেলথ ও আপটাইম) ---
def get_server_uptime():
    uptime_seconds = int(time.time() - start_time)
    days, rem = divmod(uptime_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

# --- রেসপন্স ক্লিনিং (বিস্তারিত ফিল্টার) ---
def clean_api_response(text):
    if not text:
        return None
    
    # এপিআই-এর যত প্রকার ফালতু প্রমোশন আছে সব এখানে
    garbage_list = [
        "Worm GPT", "আবদুর রহমান", "Created by", "API Developer", 
        "Telegram Channel", "Join us", "success", "DarkTube", 
        "Model:", "Response:", "Instruction:", "নমস্কার", "আদাব"
    ]
    
    # JSON থাকলে শুধু মূল উত্তর বের করা
    if isinstance(text, str) and text.strip().startswith('{'):
        try:
            json_data = json.loads(text)
            text = json_data.get('response') or json_data.get('content') or text
        except:
            pass

    lines = str(text).split('\n')
    cleaned_lines = []
    for line in lines:
        if not any(garbage.lower() in line.lower() for garbage in garbage_list):
            cleaned_lines.append(line)
    
    return "\n".join(cleaned_lines).strip()

# --- ৪টি এপিআই ফাংশন (বিস্তারিত লজিক) ---

def call_groq(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 500
        }
        res = requests.post(url, headers=headers, json=data, timeout=10)
        return res.json()['choices'][0]['message']['content']
    except:
        return None

def call_gemini(prompt):
    try:
        url = f"https://gemini-primezone.vercel.app/?q={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=10)
        return res.text if res.status_code == 200 else None
    except:
        return None

def call_worm(prompt):
    try:
        url = f"https://worm-api-seven.vercel.app/api/ask?prompt={urllib.parse.quote(prompt)}"
        res = requests.get(url, timeout=10)
        return res.text if res.status_code == 200 else None
    except:
        return None

def call_darktube(prompt):
    try:
        url = 'https://darktube.serv00.net/ai.php'
        res = requests.post(url, json={'prompt': prompt}, timeout=10)
        data = res.json()
        return data.get('response') if data.get('success') else None
    except:
        return None

# --- মেইন রিপ্লাই লজিক ---
def get_final_reply(user_input, user_name, is_owner):
    stats["total_requests"] += 1
    
    # প্রম্পটটি বড় এবং শক্তিশালী করা হয়েছে
    full_prompt = (
        f"তুমার নাম {BOT_NAMES[0]}। মেকার {OWNER_NAME}। ইউজার: {user_name}। "
        f"নির্দেশনা: ১. শুদ্ধ বাংলায় চরম ফানি রোস্ট স্টাইলে কথা বলো এবং তোমার কাজ সবাইকে হাসানো। ২. ২-৩ লাইনে উত্তর শেষ করো। "
        f"৩. মুসলিম আদব বজায় রাখো (নমস্কার/আদাব নিষিদ্ধ)। ৪. বাংলিশ বলবে না। "
        f"ইউজারের কথা: {user_input}"
    )

    # সিরিয়ালি ৪টি এপিআই চেক
    reply = call_groq(full_prompt)
    if reply:
        stats["groq_hits"] += 1
        stats["last_api"] = "Groq (Llama)"
    else:
        reply = call_gemini(full_prompt)
        if reply:
            stats["gemini_hits"] += 1
            stats["last_api"] = "Gemini Prime"
        else:
            reply = call_worm(full_prompt)
            if reply:
                stats["worm_hits"] += 1
                stats["last_api"] = "Worm GPT"
            else:
                reply = call_darktube(full_prompt)
                if reply:
                    stats["darktube_hits"] += 1
                    stats["last_api"] = "DarkTube"
                else:
                    stats["failed_hits"] += 1
                    return "সার্ভারগুলো বিরিয়ানি খাইতে গেছে বস! কেউ কাজ করছে না। 😅"

    return clean_api_response(reply)

# --- ইনলাইন অ্যাডমিন প্যানেল ---
def get_admin_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # বাটনগুলো ডিটেইলড করা হয়েছে
    btn1 = types.InlineKeyboardButton(f"Status: {'🟢 Active' if stats['is_active'] else '🔴 Off'}", callback_data="toggle_bot")
    btn2 = types.InlineKeyboardButton(f"⏳ Up: {get_server_uptime()}", callback_data="uptime_refresh")
    btn3 = types.InlineKeyboardButton(f"📊 API Performance", callback_data="api_stats")
    btn4 = types.InlineKeyboardButton(f"👥 Users: {len(all_users)}", callback_data="user_count")
    btn5 = types.InlineKeyboardButton("📢 Broadcast Message", callback_data="bc_info")
    btn6 = types.InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="refresh")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    return markup

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.username != OWNER_USERNAME:
        return
    bot.send_message(message.chat.id, "🛠 **BMT Master Dashboard**\nএখানে বটের রিয়েল-টাইম তথ্য এবং কন্ট্রোল দেওয়া আছে।", reply_markup=get_admin_markup())

@bot.callback_query_handler(func=lambda call: True)
def admin_callback(call):
    if call.from_user.username != OWNER_USERNAME: return

    if call.data == "toggle_bot":
        stats["is_active"] = not stats["is_active"]
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_admin_markup())
        bot.answer_callback_query(call.id, f"বট এখন {'চালু' if stats['is_active'] else 'বন্ধ'}")

    elif call.data == "api_stats":
        api_msg = (
            f"📈 **এপিআই পারফরম্যান্স রিপোর্ট**\n"
            f"Total Requests: {stats['total_requests']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ Groq: {stats['groq_hits']}\n"
            f"✅ Gemini: {stats['gemini_hits']}\n"
            f"✅ Worm: {stats['worm_hits']}\n"
            f"✅ DarkTube: {stats['darktube_hits']}\n"
            f"❌ Failed: {stats['failed_hits']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Last Active: {stats['last_api']}"
        )
        bot.answer_callback_query(call.id, "রিপোর্ট জেনারেট হচ্ছে...", show_alert=False)
        bot.send_message(call.message.chat.id, api_msg)

    elif call.data == "refresh":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_admin_markup())
        bot.answer_callback_query(call.id, "Dashboard Refreshed!")

# --- ব্রডকাস্ট ---
@bot.message_handler(commands=['broadcast'])
def handle_bc(message):
    if message.from_user.username != OWNER_USERNAME: return
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "ব্যবহার: `/broadcast মেসেজ`")
        return
    
    sent = 0
    for uid in all_users:
        try:
            bot.send_message(uid, f"📢 **BMT OFFICIAL NOTICE**\n\n{text}\n\n{OWNER_NAME}")
            sent += 1
        except: pass
    bot.reply_to(message, f"সফলভাবে {sent} জনের কাছে পাঠানো হয়েছে।")

# --- মেসেজ হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def main_handler(message):
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID: return
    if not message.text: return
    
    user_id = message.from_user.id
    all_users.add(user_id)
    
    is_owner = (message.from_user.username == OWNER_USERNAME)
    name_call = any(name.lower() in message.text.lower() for name in BOT_NAMES)
    is_reply = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    if message.chat.type == "private" or name_call or is_reply:
        if not stats["is_active"] and not is_owner:
            bot.reply_to(message, "বস আমাকে এখন ঘুমাতে বলছে। পরে আসিস! 💤")
            return
            
        bot.send_chat_action(message.chat.id, 'typing')
        reply_text = get_final_reply(message.text, message.from_user.first_name, is_owner)
        
        if reply_text:
            bot.reply_to(message, f"{reply_text}\n\n      {OWNER_NAME}")

bot.infinity_polling()
