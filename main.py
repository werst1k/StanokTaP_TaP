import telebot
from telebot import types
import sqlite3
import time
import threading

 
TOKEN = "8338875584:AAEwk6tzSSSj_0AmTSzt7BSa0v8shc_93TQ"
CHANNEL_ID = -1002905029977  
CHANNEL_LINK = "https://t.me/stanok_keys_promo"
ADMIN_ID = "@Werst1k"  


bot = telebot.TeleBot(TOKEN)


def init_db():
    conn = sqlite3.connect('clicker.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY, 
                      balance INTEGER DEFAULT 0,
                      last_click INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()


def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id)
        is_subscribed = status.status in ['member', 'administrator', 'creator']
        print(f"Проверка подписки для {user_id}: {is_subscribed} (статус: {status.status})")
        return is_subscribed
    except Exception as e:
        print(f"Ошибка при проверке подписки для {user_id}: {e}")
        
        bot.send_message(user_id, 
                        "❌ Ошибка проверки подписки. Убедитесь, что бот добавлен как администратор в канал.")
        return False


def create_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("💰 Клик")
    btn2 = types.KeyboardButton("📊 Баланс")
    btn3 = types.KeyboardButton("💳 Вывод")
    btn4 = types.KeyboardButton("🔄 Проверить подписку")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

def send_with_menu(chat_id, text, parse_mode='Markdown'):
    bot.send_message(chat_id, text, 
                     reply_markup=create_menu(), 
                     parse_mode=parse_mode)


def send_subscription_required(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    subscribe_btn = types.InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)
    check_btn = types.InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")
    markup.add(subscribe_btn)
    markup.add(check_btn)
    
    if message_id:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⚠️ *Для использования бота нужно подписаться на канал!*\n\n"
                     f"📢 Канал: {CHANNEL_LINK}\n\n"
                     f"1. Нажмите кнопку '📢 Подписаться на канал'\n"
                     f"2. Подпишитесь на канал\n"
                     f"3. Вернитесь в бота и нажмите '✅ Я подписался'",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.send_message(chat_id,
                            f"⚠️ *Для использования бота нужно подписаться на канал!*\n\n"
                            f"📢 Канал: {CHANNEL_LINK}\n\n"
                            f"1. Нажмите кнопку '📢 Подписаться на канал'\n"
                            f"2. Подпишитесь на канал\n"
                            f"3. Вернитесь в бота и нажмите '✅ Я подписался'",
                            reply_markup=markup,
                            parse_mode='Markdown')
    else:
        bot.send_message(chat_id,
                        f"⚠️ *Для использования бота нужно подписаться на канал!*\n\n"
                        f"📢 Канал: {CHANNEL_LINK}\n\n"
                        f"1. Нажмите кнопку '📢 Подписаться на канал'\n"
                        f"2. Подпишитесь на канал\n"
                        f"3. Вернитесь в бота и нажмите '✅ Я подписался'",
                        reply_markup=markup,
                        parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    print(f"Команда /start от {user_id} ({username})")
    
    is_subscribed = check_subscription(user_id)
    
    if not is_subscribed:
        send_subscription_required(message.chat.id)
        return
    
    conn = sqlite3.connect('clicker.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", 
                   (user_id, 0))
    conn.commit()
    conn.close()
    
    send_with_menu(message.chat.id,
                  f"👋 *Привет, {username}!*\n\n"
                  "🎮 *Добро пожаловать в кликер!*\n\n"
                  "✨ *Доступные действия:*\n"
                  "• *💰 Клик* — заработать голду (+100 за клик)\n"
                  "• *📊 Баланс* — посмотреть свой баланс\n"
                  "• *💳 Вывод* — вывести голду\n"
                  "• *🔄 Проверить подписку* — обновить статус подписки\n\n"
                  "🏆 *Минимальный вывод:* 1000 голды")


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name
    
    print(f"Проверка подписки по кнопке от {user_id} ({username})")
    
   
    bot.answer_callback_query(call.id, "🔍 Проверяем подписку...")
    
    
    is_subscribed = check_subscription(user_id)
    
    if is_subscribed:
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
       
        conn = sqlite3.connect('clicker.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", 
                       (user_id, 0))
        conn.commit()
        conn.close()
        
        send_with_menu(call.message.chat.id,
                      f"✅ *Отлично, {username}!*\n\n"
                      "Теперь у вас есть доступ ко всем функциям бота!\n\n"
                      "Выберите действие в меню ниже ↓")
    else:
 
        send_subscription_required(call.message.chat.id, call.message.message_id)
        
        
        bot.answer_callback_query(
            call.id, 
            "❌ Вы еще не подписались на канал!\n\n"
            "1. Нажмите кнопку 'Подписаться на канал'\n"
            "2. Подпишитесь\n"
            "3. Нажмите 'Я подписался' еще раз", 
            show_alert=True
        )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    print(f"Сообщение от {user_id} ({username}): {message.text}")
    
 "Проверить подписку"
    if message.text == "🔄 Проверить подписку":
        is_subscribed = check_subscription(user_id)
        if is_subscribed:
            send_with_menu(message.chat.id, "✅ *Вы подписаны на канал!*\nДоступ ко всем функциям открыт.")
        else:
            send_subscription_required(message.chat.id)
        return
    

    is_subscribed = check_subscription(user_id)
    
    if not is_subscribed:
        send_subscription_required(message.chat.id)
        return
    
    conn = sqlite3.connect('clicker.db', check_same_thread=False)
    cursor = conn.cursor()
    
    if message.text == "💰 Клик":
        
        cursor.execute("SELECT last_click, balance FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        
        if result:
            last_click, balance = result
        else:
           
            cursor.execute("INSERT INTO users (user_id, balance, last_click) VALUES (?, 0, 0)", (user_id,))
            last_click, balance = 0, 0
            conn.commit()
        
        current_time = int(time.time())
        if current_time - last_click < 1:
            send_with_menu(message.chat.id, "⏳ *Кликайте немного медленнее!*\nМаксимум 1 клик в секунду.")
        else:
            
            new_balance = balance + 100
            cursor.execute("UPDATE users SET balance=?, last_click=? WHERE user_id=?", 
                          (new_balance, current_time, user_id))
            conn.commit()
            
            send_with_menu(message.chat.id, 
                          f"✅ *+100 голды!*\n"
                          f"💰 Текущий баланс: *{new_balance} голды*")
    
    elif message.text == "📊 Баланс":
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        balance = result[0] if result else 0
        
        send_with_menu(message.chat.id, 
                      f"💰 *Ваш баланс:*\n"
                      f"🏆 *{balance} голды*\n\n"
                      f"📈 До минимального вывода: *{max(0, 1000 - balance)} голды*")
    
    elif message.text == "💳 Вывод":
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        balance = result[0] if result else 0
        
        if balance < 1000:
            send_with_menu(message.chat.id, 
                          f"❌ *Недостаточно средств для вывода!*\n\n"
                          f"💰 Ваш баланс: *{balance} голды*\n"
                          f"🏆 Минимальная сумма вывода: *1000 голды*\n\n"
                          f"📈 Необходимо еще: *{1000 - balance} голды*\n"
                          f"✨ Это примерно *{max(1, (1000 - balance) // 100)} кликов*")
        else:
            
            user_link = f"@{username}" if message.from_user.username else f"[{username}](tg://user?id={user_id})"
            
            send_with_menu(message.chat.id,
                          f"💼 *Запрос на вывод*\n\n"
                          f"👤 Пользователь: {user_link}\n"
                          f"💰 Сумма к выводу: *{balance} голды*\n"
                          f"🆔 ID: `{user_id}`\n\n"
                          f"📋 *Инструкция:*\n"
                          f"1. Сохраните эту информацию\n"
                          f"2. Отправьте администратору: {ADMIN_ID}\n"
                          f"3. Ожидайте обработки заявки\n\n"
                          f"⏰ Обычно обработка занимает до 24 часов\n"
                          f"📞 Контакт: {ADMIN_ID}")
    
    else:

        send_with_menu(message.chat.id,
                      "🤖 *Доступные команды:*\n\n"
                      "• *💰 Клик* — заработать голду\n"
                      "• *📊 Баланс* — посмотреть баланс\n"
                      "• *💳 Вывод* — вывести средства\n"
                      "• *🔄 Проверить подписку* — обновить статус")
    
    conn.close()


if __name__ == "__main__":
    print("🟢 Бот запускается...")
    print(f"ID канала: {CHANNEL_ID}")
    print(f"Ссылка на канал: {CHANNEL_LINK}")
    

    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот: @{bot_info.username}")
        
        
        try:
            chat_member = bot.get_chat_member(CHANNEL_ID, bot_info.id)
            print(f"📊 Статус бота в канале: {chat_member.status}")
        except Exception as e:
            print(f"⚠️ Внимание! Бот не может получить доступ к каналу: {e}")
            print("✅ Убедитесь, что:")
            print("1. Бот добавлен в канал как администратор")
            print("2. У бота есть права 'Может видеть участников'")
            print("3. Канал публичный или бот добавлен в приватный канал")
    except Exception as e:
        print(f"❌ Ошибка получения информации о боте: {e}")
    
    init_db()
    print("✅ База данных готова")
    
    print("🤖 Бот работает...")
    print("=" * 50)
    
    while True:
try:
    bot_info = bot.get_me()
    print(f"Бот: @{bot_info.username}")
    
    
    chat_member = bot.get_chat_member(CHANNEL_ID, bot_info.id)
    print(f"Статус бота в канале: {chat_member.status}")
except Exception as e:
    print(f"Ошибка: {e}")

 bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
