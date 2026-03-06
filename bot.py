import telebot
import requests

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8626861144:AAGBFKDBubylAXt2tNpm9iru2pm-P4La4aI"
WORM_API_URL = "https://worm-api-seven.vercel.app/api/ask"

# আপনার গ্রুপের চ্যাট আইডি এখানে দিন (আইডিটি -১০০ দিয়ে শুরু হবে)
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
                        f"আমাদের গ্রুপে আপনাকে স্বাগতম। আশা করি আমাদের সাথে আপনার সময়টা দারুণ কাটবে!\n\n"
                        f"{OWNER_NAME}")
        bot.reply_to(message, welcome_text)

# Worm API থেকে রেসপন্স নেওয়ার ফাংশন
def get_worm_response(user_input, user_name, is_owner):
    owner_context = "তুমি এখন তোমার মালিকের সাথে কথা বলছো, তাকে সম্মান দিয়ে 'বস' ডাকো।" if is_owner else "তুমি একজন সাধারণ ইউজারের সাথে কথা বলছো।"
    
    # API এর জন্য প্রম্পট তৈরি
    full_prompt = (
        f"তোমার নাম {BOT_NAMES[0]}। তোমার মেকার {OWNER_NAME}। "
        f"ইউজার নাম: {user_name}। {owner_context} "
        f"নির্দেশনা: ১. শুধুমাত্র শুদ্ধ বাংলা ও মজার ভাষায় কথা বলো। "
        f"২. প্রতিটি উত্তরের শেষে ৫-৬টি স্পেস দিয়ে '{OWNER_NAME}' লেখাটি যুক্ত করো। "
        f"৩. ইউজার ইনপুট: {user_input}"
        f"৪. সবাইকে হাসানো তেমার কাজ। লেখাতে ইমোজি ব্যবহার করবে।"
    )

    try:
        # API কল (GET Request)
        response = requests.get(WORM_API_URL, params={"prompt": full_prompt})
        if response.status_code == 200:
            # API যদি সরাসরি টেক্সট দেয় তবে response.text, আর JSON দিলে response.json() ব্যবহার করতে হয়
            # সাধারণত এই ধরনের API response['content'] বা response['message'] এ উত্তর দেয়।
            # যদি API শুধু টেক্সট পাঠায় তবে নিচের লাইনটি কাজ করবে:
            data = response.json()
            return data.get("response", "বুঝতে পারছি না রে ভাই!") 
        else:
            return "সার্ভার একটু বিজি, পরে ট্রাই করো! 😅"
    except:
        return "নেটওয়ার্কের সমস্যা হচ্ছে!"

# ২. মেসেজ হ্যান্ডেলার
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # নিরাপত্তা: শুধুমাত্র নির্দিষ্ট গ্রুপ এবং পার্সোনাল চ্যাটে কাজ করবে
    if message.chat.type != "private" and message.chat.id != ALLOWED_GROUP_ID:
        return 

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
        reply = get_worm_response(user_text, user_name, is_owner)
        bot.reply_to(message, reply)

print(f"বট এখন Worm API দিয়ে আপনার গ্রুপে অ্যাক্টিভ!")
bot.infinity_polling()
