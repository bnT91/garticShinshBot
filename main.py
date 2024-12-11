import telebot
from telebot import types

bot = telebot.TeleBot('7892869505:AAEMltK8z1DRKhMjJ5HsU_IhTwGss7GDxZs')

allowed_users = []
game = False

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
        if game:
            print("Напишите /join, чтобы присоединиться к текущей игре. ")
        else:
            print("На данный момент игра не запущена. Напишите /create для создания новой.")


@bot.callback_query_handler()
def query_callback(callback):
    if callback.data[:11] == "accept_user":
        allowed_users.append(int(callback.data[12:]))
        with open("allowed_users.txt", "a") as f:
            f.write(callback.data[12:] + '\n')
        bot.send_message(int(callback.data[12:]), "🔓✅ Доступ разрешён!")
    elif callback.data[:12] == "decline_user":
        bot.send_message(int(callback.data[13:]), "❌Доступ запрещён.")


bot.polling(non_stop=True)
