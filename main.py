"""

 Coding Lovers team

 Find us on:
 Telegram: https://t.me/CodingLovers_OFF
 YouTube: https://www.youtube.com/@CodingLovers
 Instagram: https://www.instagram.com/codinglovers_off/

"""

# This is a Python code for a Telegram bot that provides support services. Here's the breakdown:

# Importing necessary libraries
import re
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, ForceReply
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from telebot import custom_filters
from expiringdict import ExpiringDict

from config import BOT_TOKEN, SUPPORT_ID

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(token=BOT_TOKEN, state_storage=state_storage, parse_mode="HTML")

# Declaring a global lists to keep track of chat ids and texts
texts = ExpiringDict(max_len=1000, max_age_seconds=2592000)

class Support(StatesGroup):
    text = State()
    respond = State()

# Function to escape all special characters with a backslash
def escape_special_characters(text):
    special_characters = r"([\*\_\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])"
    return re.sub(special_characters, r'\\\1', text)

# Handling start command
@bot.message_handler(commands=['start'])
def start(m: Message):
    print(m.reply_to_message)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Support 👨🏻‍💻")

    bot.send_message(chat_id=m.chat.id, text=f"Hello <b>{m.from_user.first_name}</b>", reply_markup=markup)

# Handling the 'Support 👨🏻‍💻' button click event
@bot.message_handler(func= lambda m: m.text== "Support 👨🏻‍💻")
def sup(m: Message):
    bot.send_message(chat_id=m.chat.id, text="Send your message to support:")
    bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=m.chat.id)    

# Handling the user's first message which is saved in 'Support.text' state
@bot.message_handler(state=Support.text)
def sup_text(m: Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="answer", callback_data="answer"))

    bot.send_message(chat_id=SUPPORT_ID, text=f"Recived a message from <code>{m.from_user.id}</code> with username @{m.from_user.username}:\n\nMessage text:\n<b>{escape_special_characters(m.text)}</b>", reply_markup=markup)

    bot.send_message(chat_id=m.chat.id, text="Your message was sent!")

    texts[m.from_user.id] = m.text

    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# Handling the callback query when the 'answer' button is clicked
@bot.callback_query_handler(func= lambda call: call.data == "answer")
def answer(call: CallbackQuery):
    pattern = r"Recived a message from \d+"
    user = re.findall(pattern=pattern, string=call.message.text)[0].split()[4]
    
    bot.send_message(chat_id=call.message.chat.id, text=f"Send your answer to <code>{user}</code>:", reply_markup=ForceReply())

    bot.set_state(user_id=call.from_user.id, state=Support.respond, chat_id=call.message.chat.id)

# Handling the support agent's reply message which is saved in 'Support.respond' state
@bot.message_handler(state=Support.respond, func= lambda m: m.reply_to_message.text.startswith("Send your answer to"))
def answer_text(m: Message):
    pattern = r"Send your answer to \d+"
    user = int(re.findall(pattern=pattern, string=m.reply_to_message.text)[0].split()[4])

    try:
        try:
            user_message = texts[user]
            bot.send_message(chat_id=user, text=f"Your message:\n<i>{escape_special_characters(user_message)}</i>\n\nSupport answer:\n<b>{escape_special_characters(m.text)}</b>")
            bot.send_message(chat_id=m.chat.id, text="Your answer was sent!")

            del texts[user]
            bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)
        
        except:
            bot.send_message(chat_id=user, text=f"Support answer:\n<b>{escape_special_characters(m.text)}</b>")
            bot.send_message(chat_id=m.chat.id, text="Your answer was sent!")

            bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)
        
    except Exception as e:
        bot.send_message(chat_id=m.chat.id, text=f"Something goes wrong...\n\nException:\n<code>{e}</code>")

# Starting the bot and adding the state filter as a custom filter
if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling()
