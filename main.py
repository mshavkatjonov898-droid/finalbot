import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN, state_storage=telebot.storage.StateMemoryStorage())
bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))

SAVOLLAR = [["Python'da ro'yxat qaysi qavsda yoziladi?", ["( )", "[ ]", "{ }"], 1],
["2 ** 3 nechaga teng?", ["6", "8", "9"], 1],
["Bot tokenini kim beradi?", ["@BotFather", "@Python", "Google"], 0],]

class Quiz(telebot.handler_backends.StatesGroup):
    ism = telebot.handler_backends.State()
    savol = telebot.handler_backends.State()

def menyu():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎮 Boshlash", "ℹ️ Yordam")
    return kb

def savol_yubor(chat_id, i):
    matn, variantlar, _ = SAVOLLAR[i]
    kb = telebot.types.InlineKeyboardMarkup()
    for j, v in enumerate(variantlar):
        kb.add(telebot.types.InlineKeyboardButton(v, callback_data=f"javob_{j}"))
    bot.send_message(chat_id, f"{i + 1}-savol: {matn}", reply_markup=kb)

@bot.message_handler(commands=["start"])
def start(message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Salom! Mini viktorinaga xush kelibsiz.", reply_markup=menyu())

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def yordam(message):
    bot.send_message(message.chat.id,"Boshlash — 3 ta savol. Javob tugmasini bosing.\n/cancel — to'xtatish",)

@bot.message_handler(commands=["test"])
def test(message):
    savol_yubor(message.chat.id, 0)

@bot.message_handler(commands=["cancel"], state="*")
def cancel(message):
    uid, cid = message.from_user.id, message.chat.id
    if bot.get_state(uid, cid) is None:
        return boshqa(message)
    bot.delete_state(uid, cid)
    bot.send_message(cid, "❌ To'xtatildi", reply_markup=menyu())

@bot.message_handler(func=lambda m: m.text == "🎮 Boshlash")
def boshlash(message):
    bot.set_state(message.from_user.id, Quiz.ism, message.chat.id)
    bot.send_message(message.chat.id, "Ismingiz?", reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(state=Quiz.ism)
def ism_qabul(message):
    uid, cid = message.from_user.id, message.chat.id
    bot.set_state(uid, Quiz.savol, cid)
    with bot.retrieve_data(uid, cid) as data:
        data["ism"] = message.text
        data["i"] = 0
        data["ball"] = 0
    savol_yubor(cid, 0)

@bot.message_handler(state=Quiz.savol)
def savol_matn(message):
    bot.send_message(message.chat.id, "Tugmalardan birini bosing 👆 (yoki /cancel)")

@bot.callback_query_handler(func=lambda c: c.data.startswith("javob_"))
def javob(call):
    uid, cid = call.from_user.id, call.message.chat.id

    if bot.get_state(uid, cid) != Quiz.savol.name:
        bot.answer_callback_query(call.id, "O'yin tugagan. 🎮 Boshlash ni bosing")
        return

    tanlov = int(call.data.split("_")[1])
    with bot.retrieve_data(uid, cid) as data:
        i = data["i"]
        togri = SAVOLLAR[i][2]
        if tanlov == togri:
            data["ball"] += 1
            belgi = "✅ To'g'ri!"
        else:
            belgi = f"❌ Xato. To'g'ri javob: {SAVOLLAR[i][1][togri]}"
        data["i"] = i + 1
        keyingi, ism, ball = data["i"], data["ism"], data["ball"]

    bot.edit_message_text(f"{i + 1}-savol: {SAVOLLAR[i][0]}\n{belgi}", cid,call.message.message_id,)
    bot.answer_callback_query(call.id)

    if keyingi < len(SAVOLLAR):
        savol_yubor(cid, keyingi)
    else:
        bot.delete_state(uid, cid)
        bot.send_message(cid, f"{ism}, natijangiz: {ball}/{len(SAVOLLAR)}", reply_markup=menyu())

@bot.message_handler(func=lambda m: True)
def boshqa(message):
    bot.send_message(message.chat.id, "Tushunmadim 🤔 Pastdagi tugmalardan foydalaning", reply_markup=menyu())

bot.infinity_polling()