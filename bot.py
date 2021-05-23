import sys
from mysql.connector import cursor
import telebot
import mysql.connector
from mysql.connector import errorcode

# Telegram token
bot = telebot.TeleBot("1787236564:AAGv_PwY13rM_1QN9aPJbKWWGpQx726AvMM")
# получить id канала/группы
# print(bot.get_chat('@vladneverovyoutube').id)


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
# cursor.execute("DROP TABLE regs")
# cursor.execute("CREATE TABLE regs (id INT AUTO_INCREMENT PRIMARY KEY, \
#     first_name VARCHAR(255), \
#     last_name VARCHAR(255), \
#     description VARCHAR(255), user_id INT(11))")

user_data = {}

# cursor.execute("CREATE DATABASE dbbot")
# cursor.execute("CREATE DATABASE watchman")
# cursor.execute("SHOW DATABASES")

#for x in cursor:
#    print(x)

#cursor.execute("CREATE TABLE users (first_name VARCHAR(255), last_name VARCHAR(255))")
# cursor.execute("SHOW TABLES")

#for x in cursor:
#    print(x)

#cursor.execute("ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")


# sql = "INSERT INTO users (first_name, last_name, user_id) VALUES (%s, %s, %s)"
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

# sql = "SELECT \
#     users.first_name AS user, \
#     user_groups.title AS user_group \
#     FROM users \
#     JOIN user_groups ON users.user_group_id = user_groups.id"

# cursor.execute(sql)
# users = cursor.fetchall()

# for user in users:
#     print(user)


class User:
    def __init__(self, first_name):
        self.first_name = first_name
        self.last_name = ''
        self.description = ''

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
        msg = bot.reply_to(message, """\
        Привет, я бот-охранник в Istra Village.
        """)

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

        msg = bot.send_message(message.chat.id, 'Напишите описание')
        bot.register_next_step_handler(msg, process_description_step)

    except Exception as e:
        bot.reply_to(message, 'oooops')

def process_description_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.description = message.text

        # Проверка есть ли пользователь в БД
        sql = "SELECT * FROM users WHERE user_id = {0}".format(user_id)
        cursor.execute(sql)
        existsUser = cursor.fetchone()

        # Если нету, то добавить в БД
        if (existsUser == None):
               sql = "INSERT INTO users (first_name, last_name, telegram_user_id) \
                                  VALUES (%s, %s, %s)"
               val = (message.from_user.first_name, message.from_user.last_name, user_id)
               cursor.execute(sql, val)

        # Регистрация заявки
        sql = "INSERT INTO regs (first_name, last_name, description, user_id) \
                                  VALUES (%s, %s, %s, %s)"
        val = (user.first_name, user.last_name, user.description, user_id)
        cursor.execute(sql, val)
        db.commit()


        bot.send_message(message.chat.id, "Вы успешно зарегистрированны!")

    except Exception as e:
        bot.reply_to(message, 'oooops')
# make some difference

# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop = True)