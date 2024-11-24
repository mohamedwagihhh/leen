import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

# بيانات البوت
BOT_TOKEN = "5167943610:AAGc7xugCtSGtAP_8gmVBl0FQWxRJNRtgnI"
FIREBASE_URL = "https://drugguide-6a6ea-default-rtdb.firebaseio.com/"

# إعداد Flask
app = Flask(__name__)

# إعداد البوت والـ Dispatcher
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=4)

# إعداد الـ Logging
logging.basicConfig(level=logging.INFO)

# تعريف الأوامر
def start(update, context):
    update.message.reply_text("أهلا وسهلا! 😊\nأنا بوت بحث الأدوية في مصر.\nاكتب اسم الدواء لبدء البحث 🔍.")

def help_command(update, context):
    update.message.reply_text(
        "الأوامر المتاحة:\n"
        "/start - بدء المحادثة\n"
        "/help - المساعدة\n"
        "اكتب اسم أي دواء للبحث عن التفاصيل."
    )

def search_drugs(update, context):
    query = update.message.text.strip().lower()
    if not query:
        update.message.reply_text("من فضلك اكتب اسم الدواء الذي تريد البحث عنه.")
        return

    import requests
    try:
        response = requests.get(f"{FIREBASE_URL}.json")
        response.raise_for_status()
        data = response.json()

        results = [
            item for item in data.values() if query in item.get("arabic", "").lower()
        ]

        if results:
            reply = "نتائج البحث:\n\n"
            for result in results[:5]:  # عرض أول 5 نتائج فقط
                reply += (
                    f"الاسم: {result.get('name', 'غير متوفر')}\n"
                    f"الاسم بالعربية: {result.get('arabic', 'غير متوفر')}\n"
                    f"الشركة: {result.get('company', 'غير متوفر')}\n"
                    f"السعر القديم: {result.get('oldprice', 'غير متوفر')} جنيه\n"
                    f"السعر الحالي: {result.get('price', 'غير متوفر')} جنيه\n"
                    f"الشكل الدوائي: {result.get('dosage_form', 'غير متوفر')}\n"
                    f"الوصف: {result.get('description', 'غير متوفر')}\n"
                    f"المادة الفعالة: {result.get('active', 'غير متوفر')}\n"
                    f"التصنيف الدوائي: {result.get('pharmacology', 'غير متوفر')}\n"
                    f"طريقة الاستخدام: {result.get('route', 'غير متوفر')}\n"
                    f"الوحدات: {result.get('units', 'غير متوفر')}\n\n"
                )
            update.message.reply_text(reply)
        else:
            update.message.reply_text("لم يتم العثور على أي نتائج مطابقة.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        update.message.reply_text("حدث خطأ أثناء جلب البيانات. حاول مرة أخرى لاحقاً.")

# إضافة الـ Handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("search", search_drugs))  # بحث عادي بالنص

# إعداد الـ Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"

# Route رئيسي لاختبار الخدمة
@app.route("/")
def index():
    return "البوت يعمل بنجاح!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
