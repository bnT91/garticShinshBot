import telebot
from telebot import types
import random as rand
from time import sleep

bot = telebot.TeleBot('7892869505:AAEMltK8z1DRKhMjJ5HsU_IhTwGss7GDxZs')

allowed_users = []
game = False
prep = False
players = []
words = {}
last_words = []
stories = []
creator = None
giving = {}

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
    if message.from_user.id in allowed_users:
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
    if message.from_user.id in allowed_users:
        global players
        if prep:
            if message.from_user.id not in players:
                bot.send_message(message.chat.id, "🔗Вы присоединились. Когда создатель игры напишет /process, она начнётся. ")
                for player in players:
                    bot.send_message(player, f"Игрок <b>{message.from_user.first_name} {message.from_user.last_name}</b> присоединился!",
                                     parse_mode="html")
                players.append(message.from_user.id)
            else:
                bot.send_message(message.chat.id, "Вы уже в игре. Ожидайте начала.")
        elif game:
            bot.send_message(message.chat.id, "К сожалению, вы не можете присоединиться к уже начатой игре. 🔚Пожалуйста, дождитесь её конца.")
        else:
            bot.send_message(message.chat.id, "В данный момент игры не существует. Чтобы создать новую, напишите /create.")


@bot.message_handler(commands=["process"])
def process(message):
    if message.from_user.id in allowed_users:
        global prep, game
        global words, giving
        if prep:
            if message.from_user.id == creator:
                game = True
                prep = False
                words = {i: None for i in players}
                bot.send_message(message.chat.id, "Игра началась! Для её остановки напишите /abort.")
                for player in players:
                    giving[player] = None
                for player in players:
                    if player != creator:
                        bot.send_message(player, "Создатель игры начинает её!")
                    bot.send_sticker(player, r"CAACAgIAAxkBAAEK2vVnWm82vTns4GHMz6NFmF6ePHXl_wACpUgAAtXJmEgxSgjp7qwRmDYE")
                    mesg = bot.send_message(player, "Напишите любое предложение. Можете дать волю фантазии и начать историю!")
                    bot.register_next_step_handler(mesg, lambda msg: next_sentence(msg))
            else:
                bot.send_message(message.chat.id, "Не Вы создали данную игру. 🕔Ожидайте подтверждения админа для старта.")


@bot.message_handler(commands=["abort"])
def abort(message):
    global game, prep, players, words, last_words, stories, creator
    if message.from_user.id in [creator, 5401218650] and game:
        for player in players:
            bot.send_message(player, "👾☎️Итак, игра окончена! Подводим результаты.")
        for story in stories:
            for p in players:
                bot.send_message(p, "\n".join(story))

        game = False
        prep = False
        players.clear()
        words.clear()
        last_words.clear()
        stories.clear()
        giving.clear()
        creator = None


def next_sentence(message):
    global words, last_words, stories, giving

    if message.text == "/abort":
        abort(message)

    if message.from_user.id not in words.keys():
        return

    if not words[message.from_user.id] and game:
        message, last = message, giving[message.from_user.id]
        if not last:
            words[message.from_user.id] = [message.text, None]
        else:
            words[message.from_user.id] = [message.text, last]
        cnt = len(words) - sum([1 if not i else 0 for i in words.values()])
        for player in players:
            if player != message.from_user.id:
                bot.send_message(player, f"<b>{message.from_user.first_name} {message.from_user.last_name
                if message.from_user.last_name else "=)"}</b> "
                                         f"написал своё предложение. Сделали свой ход: <i>"
                                         f"{cnt}/{len(players)}</i>.", parse_mode="html")
        bot.send_message(message.chat.id, f"Ваше предложение принято. На данный момент сделали свой ход: <i>{cnt}/{len(players)}</i>.",
                                parse_mode="html")

        # while len(words) - sum([0 if not i else 1 for i in words.values()]) > 0:
        #     sleep(0.3)
        #     # print(len(players), words)
        #     last_words = list(words.values())

        if len(words) == sum([0 if not i else 1 for i in words.values()]):

            last_words = list(words.values())
            # print(last_words)
            for w in words.keys():
                words[w] = None

            if not last:
                stories = [[w[0]] for w in last_words]
            else:
                for wrd in last_words:
                    for stss in range(len(stories)):
                        st = stories[stss]
                        if st[-1] == wrd[1]:
                            stories[stss].append(wrd[0])

            crash = last_words.copy()
            rand.shuffle(crash)
            for id in range(len(players)):
                wrd = crash[id]
                player = players[id]
                mesg = bot.send_message(player, f"Продолжите: <i>{str(wrd[0])}</i>", parse_mode="html")
                giving[player] = wrd[0]
                bot.register_next_step_handler(mesg, lambda msg: next_sentence(msg))


while True:
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(e)
