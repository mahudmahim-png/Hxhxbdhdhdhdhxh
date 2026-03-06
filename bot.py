import telebot
import requests

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8626861144:AAGBFKDBubylAXt2tNpm9iru2pm-P4La4aI"
GROQ_API_KEY = "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"

# আপনার গ্রুপের চ্যাট আইডি এখানে দিন (উদাহরণ: -100123456789)
ALLOWED_GROUP_ID = -1002909181457 

BOT_NAMES = ["bmt", "Bmt", "BMT"]  
OWNER_NAME = " - 𝚃𝙴𝙰𝙼 𝙱𝙼𝚃⸝⸝⸝♡"
OWNER_USERNAME = "Unkonwn_BMT" # @ বাদে ইউজারনেম

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ১. নতুন মেম্বার জয়েন করলে ওয়েলকাম (শুধুমাত্র নির্দিষ্ট গ্রুপে)
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return
    
    for member in message.new_chat_members:
        welcome_text = (f"আসসালামু আলাইকুম {member.first_name} ভাই/আপু! 😊\n"
                        f"আমাদের গ্রুপে আপনাকে স্বাগতম। আশা করি এখানে আপনার সময়টা দারুণ কাটবে!\n\n"
                        f"{OWNER_NAME}")
        bot.reply_to(message, welcome_text)

# Groq API ফাংশন
def get_groq_response(user_input, user_name, is_owner):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    owner_status = "তিনি তোমার পরম শ্রদ্ধেয় মালিক, তাকে বস বলে সম্বোধন করো।" if is_owner else "তিনি একজন সাধারণ ইউজার।"

    system_prompt = f"""
    তোমার নাম {BOT_NAMES[0]}। তোমাকে তৈরি করেছে {OWNER_NAME}। 
    ইউজারের নাম: {user_name}। {owner_status}
    
    নির্দেশনা:
    ১. শুধুমাত্র শুদ্ধ বাংলা এবং খুব মজার ও চটপটে ভাষায় কথা বলবে।
    ২. মালিক ({OWNER_USERNAME}) মেসেজ দিলে তাকে সর্বোচ্চ সম্মান দিবে।
    ৩. প্রতিটি উত্তরের শেষে অবশ্যই ৫-৬টি স্পেস দিয়ে "{OWNER_NAME}" লিখবে।
    ৪. কেউ তোমার নাম নিলে সরাসরি তার নাম ধরে মজার উত্তর দিবে।
    """

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": user_input}],
        "temperature": 0.8
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else "সার্ভার একটু বিজি গো!"
    except:
        return "নেটওয়ার্কের সমস্যা হচ্ছে!"

# ২. মেসেজ হ্যান্ডেলার (নিরাপত্তা সহ)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # নিরাপত্তা চেক: শুধুমাত্র নির্দিষ্ট গ্রুপ এবং পার্সোনাল চ্যাটে কাজ করবে
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID:
        return # অন্য গ্রুপে হলে কোনো রিপ্লাই দিবে না

    if not message.text: return
    
    user_text = message.text
    user_name = message.from_user.first_name
    user_username = message.from_user.username
    
    is_owner = (user_username == OWNER_USERNAME)
    name_detected = any(name.lower() in user_text.lower() for name in BOT_NAMES)
    is_reply_to_bot = (message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)

    # রেসপন্স লজিক
    if message.chat.type == "private" or name_detected or is_reply_to_bot:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_groq_response(user_text, user_name, is_owner)
        bot.reply_to(message, reply)

print(f"বট এখন রেডি এবং শুধুমাত্র আপনার গ্রুপেই কথা বলবে!")
bot.infinity_polling()
