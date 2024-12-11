import telebot
from telebot import types

bot = telebot.TeleBot('7892869505:AAEMltK8z1DRKhMjJ5HsU_IhTwGss7GDxZs')

allowed_users = []
game = False
prep = False
players = []
creator = None

with open("allowed_users.txt", "r") as f:
    for line in f:
        allowed_users.append(int(line.strip()))


@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.id not in allowed_users:
        bot.send_message(message.chat.id, "🔒 Доступ заблокирован.\n\nЗапрос отправлен администратору, "
                                          "пожалуйста, ожидайте.")

        markup = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton("Да", callback_data=f"accept_user {message.from_user.id}")
        no = types.InlineKeyboardButton("Нет", callback_data=f"decline_user {message.from_user.id}")
        markup.row(yes, no)
        bot.send_message(5401218650, f"Добавить пользователя <b>{message.from_user.first_name} "
                                     f"{message.from_user.last_name}</b> в белый список?", parse_mode="html",
                         reply_markup=markup)

    else:
        if prep:
            bot.send_message(message.chat.id, "🔗Напишите /join, чтобы присоединиться к текущей игре. ")
        elif not game:
            bot.send_message(message.chat.id, "На данный момент игра не запущена. ➕Напишите /create для создания новой.")
        else:
            bot.send_message(message.chat.id, "Игра уже идёт. 🔚Пожалуйста, дождитесь её окончания и присоединитесь к новой / создайте её.")


@bot.callback_query_handler()
def query_callback(callback):
    if callback.data[:11] == "accept_user":
        allowed_users.append(int(callback.data[12:]))
        with open("allowed_users.txt", "a") as f:
            f.write(callback.data[12:] + '\n')
        bot.send_message(int(callback.data[12:]), "🔓✅ Доступ разрешён!")
    elif callback.data[:12] == "decline_user":
        bot.send_message(int(callback.data[13:]), "❌Доступ запрещён.")


@bot.message_handler(commands=["create"])
def create(message):
    global game, prep, players, creator
    if prep:
        bot.send_message(message.chat.id, "Игра уже создана. 🔗Чтобы присоединиться, напишите /join.")

    elif not game:
        bot.send_message(message.chat.id, "🎲🎮Вы создали новую игру. Сейчас участвуете только Вы. Каждый игрок, кто напишет /join, присоединится. "
                                          "Когда Вы посчитаете, что набралось достаточное количество участников, напишите /process и игра начнётся. ")
        creator = message.from_user.id
        players.append(creator)
        prep = True

    else:
        bot.send_message(message.chat.id, "Игра уже идёт. Пожалуйста, дождитесь её окончания и попробуйте ещё раз.")


@bot.message_handler(commands=["join"])
def join(message):
    global players
    if prep:
        if message.from_user.id not in players:
            bot.send_message(message.chat.id, "🔗Вы присоединились. Когда создатель игры напишет /process, она начнётся. ")
            players.append(message.from_user.id)
        else:
            bot.send_message(message.chat.id, "Вы уже в игре. Ожидайте начала.")
    elif not game:
        bot.send_message(message.chat.id, "К сожалению, вы не можете присоединиться к уже начатой игре. 🔚Пожалуйста, дождитесь её конца.")
    else:
        bot.send_message(message.chat.id, "В данный момент игры не существует. Чтобы создать новую, напишите /create.")


@bot.message_handler(commands=["process"])
def process(message):
    global prep, game
    if prep:
        if message.from_user.id == creator:
            game = True
            prep = False
            bot.send_message(message.chat.id, "Игра началась! Для её остановки напишите /abort.")
        else:
            bot.send_message(message.chat.id, "Не Вы создали данную игру. 🕔Ожидайте админа для старта.")


bot.polling(non_stop=True)
