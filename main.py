from time import sleep
from random import choice
import db
from telebot import TeleBot


players = []
night = True
game = False
TOKEN = '6509046593:AAES2cMAfrNBaYX-Njw4TSk5OIYEHYlEjU8'
bot = TeleBot(TOKEN)

def get_killed(night):
    if not night:
        return f"Выгнан {db.citizen_kill()}"
    else:
        return f"Убит {db.mafia_kill()}"

def game_loop(message):
    global night
    bot.send_message(message.chat.id, 'Добро пожаловать в игру! Вам даётся 2 минуты, чтобы познакомиться')
    sleep(120)
    while True:
        bot.send_message(message.chat.id, get_killed(night))
        if night:
            bot.send_message(message.chat.id, 'Город засыпает, просыпается мафия. Наступила ночь')
        else:
            bot.send_message(message.chat.id, 'Город просыпается. Наступил день')
        winner = db.win_or_lose()
        if winner == 'Победили горожане' or winner == 'Победила мафия':
            game = False
            bot.send_message(message.chat.id, f"Игра окончена. {winner}")
        #db.(dead=False)
        night = not night
        allived = db.get_all_allive()
        allived = '\n'.join(allived)
        bot.send_message(message.chat.id, f"Живые игроки:\n{allived}")
        sleep(120)


@bot.message_handler(commands=['start'])
def game_on(message):
    if not game:
        bot.send_message(message.chat.id, 'Если хотите играть пишите ')


@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    db.insert_player(player_id=message.from_user.id,
                     username=message.from_user.first_name)
    
@bot.message_handler(commands=['game'])
def game_start(message):
    global game
    players = db.player_amount()
    if players >= 4 and not game:
        db.set_role(players)
        players_roles = db.get_players_role(players=players)
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, role)
            if role == 'mafia':
                bot.send_message(player_id, f"Все мафии: {mafia_usernames}")
        game = True
        bot.send_message(message.chat.id, 'Игра началась!')
        return
    else:
        bot.send_message(message.chat.id, 'Людей недостаточно!')

@bot.message_handler(commands=['kick'])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_allive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан')
            return
        bot.send_message(message.chat.id, 'У вас больше нет права голосовать')
        return
    bot.send_message(message.chat.id, 'Сейчас ночь вы не можете голосовать')

@bot.message_handler(commands=['kill'])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_allive()
    mafias = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafias:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote('mafia_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан')
            return
        bot.send_message(message.chat.id, 'У вас больше нет права голосовать')
        return
    bot.send_message(message.chat.id, 'Сейчас день вы не можете голосовать')



if __name__ == '__main__':
    bot.polling(none_stop=True)