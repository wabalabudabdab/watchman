import sys
import telebot
import mysql.connector
from mysql.connector import errorcode

bot = telebot.TeleBot("1889911207:AAE-3yWmjEmFRxA5OILdifDbZ-kTv9veuaM")

try:
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="watchman",
    port="3306",
    database="watchman"  
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your name or password")
        sys.exit()
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
        sys.exit()
    else:
        print(err)
        sys.exit()



cursor = db.cursor()
user_data = {}


# cursor.execute("CREATE DATABASE watchman")
# cursor.execute("SHOW DATABASES")

#for x in cursor:
#    print(x)

#cursor.execute("CREATE TABLE users (first_name VARCHAR(255), last_name VARCHAR(255))")
#cursor.execute("SHOW TABLES")

#for x in cursor:
#    print(x)

#cursor.execute("ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")


# sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
# val = [("Серго", "Наумыч", 3), ("Матерь", "Драконов", 4), ("Добрый", "Друг", 5)]
# cursor.executemany(sql, val)
# db.commit()

# print(cursor.rowcount, "запись добавлена.")

###############################

# cursor.execute("CREATE TABLE user_groups (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))")
# sql = "INSERT INTO user_groups (title) VALUES (%s)"
# val = [('Администратор', ), ('Модератор', ), ('Пользователь', )]

# cursor.executemany(sql, val)
# db.commit()

# cursor.execute("ALTER TABLE users ADD COLUMN (user_group_id INT)")

sql = "SELECT \
    users.first_name AS user, \
    user_groups.title AS user_group \
    FROM users \
    JOIN user_groups ON users.user_group_id = user_groups.id"

cursor.execute(sql)
users = cursor.fetchall()

for user in users:
    print(user)


class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.last_name = ''

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
        msg = bot.send_message(message.chat.id, 'Введите имя')
        bot.register_next_step_handler(msg, process_firstname_step)

def process_firstname_step(message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)

        msg = bot.send_message(message.chat.id, 'Введите фамилию')
        bot.register_next_step_handler(msg, process_lastname_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def process_lastname_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.last_name = message.text

        sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
        val = (user.first_name, user.last_name, user_id)
        cursor.execute(sql, val)
        db.commit()


        msg = bot.send_message(message.chat.id, 'Вы успешно зарегистрированы')
    except Exception as e:
        bot.reply_to(message, 'Вы уже зарегистрированы')
# make some difference

# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)