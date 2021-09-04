import telebot
from telebot import apihelper
from telebot import types

from dbhelper import DBHelper
from settings import API_TOKEN, use_proxy, proxy_server, proxy_port
from params import buttons, messages, answers

bot = telebot.TeleBot(API_TOKEN, parse_mode=None)
if use_proxy :
    apihelper.proxy = {'https': 'socks5h://{}:{}'.format(proxy_server, proxy_port)}

db = DBHelper()
db.setup()

def join_message(chat_id):
    message = messages['join_message']
    players = db.get_all_players(chat_id)
    for player in players:
        men = "\n[{}](tg://user?id={})"
        men = men.format(player[3], player[1])
        message += men
    return message

def type_checker(message, target):
    type = message.chat.type
    if (type == 'group' or type == 'supergroup') and target == 'group':
        return True
    elif type == 'private' and target == 'private':
        return True
    else:
        return False

@bot.message_handler(commands=['tod_init'])
def initialize(message):
    if type_checker(message, 'group'):
        chat_id = message.chat.id
        chat_name = message.chat.title
        if db.check_group(chat_id):
            bot.reply_to(message, messages['group_in'])
        else:
            db.add_group(chat_id, chat_name)
            bot.reply_to(message, messages['register'])

@bot.message_handler(commands=['tod_newgame'])
def newgame(message):
    if type_checker(message, 'group'):
        chat_id = message.chat.id
        if db.check_group(chat_id):
            if db.check_game(chat_id):
                bot.send_message(message.chat.id, messages['in_progress'])
            else:
                db.start_game(chat_id)
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                join_btn = types.InlineKeyboardButton(text=buttons['join_btn'], callback_data="join")
                keyboard.add(join_btn)
                bot.send_message(message.chat.id, messages['join_message'], reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, messages['must_register'])


@bot.message_handler(commands=['tod_endgame'])
def endgame(message):
    if type_checker(message, 'group'):
        chat_id = message.chat.id
        if db.check_group(chat_id):
            if db.check_game(chat_id):
                db.start_game(chat_id)
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                callback_button = types.InlineKeyboardButton(text=buttons['delete_btn'], callback_data="endgame")
                keyboard.add(callback_button)
                bot.send_message(chat_id, messages['delete_message'], reply_markup=keyboard)
            else:
                bot.send_message(chat_id, messages['no_game'])
        else:
            bot.send_message(message.chat.id, messages['must_register'])



@bot.message_handler(commands=['tod_next'])
def nextgame(message):
    if type_checker(message, 'group'):
        chat_id = message.chat.id
        if db.check_group(chat_id):
            if db.count_player(chat_id) >= 2:
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                callback_button = types.InlineKeyboardButton(text=buttons["next_btn"], callback_data="next")
                keyboard.add(callback_button)
                bot.send_message(chat_id, messages['next_game'], reply_markup=keyboard)
            else:
                db.delete_all(chat_id)
                db.end_game(chat_id)
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                callback_button = types.InlineKeyboardButton(text=buttons["new_game"], callback_data="join")
                keyboard.add(callback_button)
                bot.send_message(chat_id, messages['another_game'], reply_markup=keyboard)

        else:
            bot.send_message(message.chat.id, messages['must_register'])

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'join':
        message_id = call.message.message_id
        chat_id = call.message.chat.id
        player_name = call.from_user.full_name
        user_id = call.from_user.id
        if db.check_player(chat_id, user_id) == 0:
            db.add_player(chat_id, user_id, player_name[:90])
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            join_btn = types.InlineKeyboardButton(text=buttons['join_btn'], callback_data="join")
            leave_btn = types.InlineKeyboardButton(text=buttons['leave_btn'], callback_data="leave")
            keyboard.add(join_btn, leave_btn)
            bot.answer_callback_query(call.id, answers['joined'])
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                text=join_message(chat_id), reply_markup=keyboard,
                parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, answers['already_in'])

    if call.data == 'leave':
        message_id = call.message.message_id
        chat_id = call.message.chat.id
        player_name = call.from_user.full_name
        user_id = call.from_user.id
        if db.check_player(chat_id, user_id) != 0:
            db.delete_player(user_id, chat_id)
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            join_btn = types.InlineKeyboardButton(text=buttons['join_btn'], callback_data="join")
            leave_btn = types.InlineKeyboardButton(text=buttons['leave_btn'], callback_data="leave")
            keyboard.add(join_btn, leave_btn)
            bot.answer_callback_query(call.id, answers['left'])
            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                text=join_message(chat_id), reply_markup=keyboard,
                parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, answers['not_in'])

    if call.data == 'next':
        chat_id = call.message.chat.id
        players = db.get_player(chat_id)
        player1 = players[0]
        player2 = players[1]
        men = "\n[{}](tg://user?id={})"
        p1 = men.format(player1[3], player1[1])
        p2 = men.format(player2[3], player2[1])
        bot.answer_callback_query(call.id, ':)')
        bot.edit_message_text(chat_id=chat_id,
            message_id=call.message.message_id,
            text=p1 + "\nمیپرسه از:\n" + p2,
            parse_mode="Markdown")

    if call.data == 'endgame':
        chat_id = call.message.chat.id
        db.delete_all(chat_id)
        db.end_game(chat_id)
        bot.answer_callback_query(call.id, answers['end_game'])
        bot.edit_message_text(chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=messages['game_ended'])


bot.polling()
