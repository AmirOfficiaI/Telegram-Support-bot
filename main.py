"""

 Coding Lovers team

 Find us on:
 Telegram: https://t.me/CodingLovers_OFF
 YouTube: https://www.youtube.com/@CodingLovers
 Instagram: https://www.instagram.com/codinglovers_off/

"""

# This is a Python code for a Telegram bot that provides support services. Here's the breakdown:

# Importing necessary libraries
import telebot
from telebot import types
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from telebot import custom_filters
import re

from config import BOT_TOKEN, SUPPORT_ID

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(token=BOT_TOKEN, state_storage=state_storage)

# Declaring two global lists to keep track of chat ids and texts
chat_ids = []
texts = {}

class Support(StatesGroup):
    text = State()
    respond = State()

# Function to escape all special characters with a backslash
def escape_special_characters(text):
    special_characters = r"([\*\_\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])"
    return re.sub(special_characters, r'\\\1', text)

# Handling start command 
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Support 👨🏻‍💻")
 
    bot.send_message(chat_id=m.chat.id, text=f"Hello *{m.from_user.first_name}*", reply_markup=markup, parse_mode="MarkdownV2")

# Handling the 'Support 👨🏻‍💻' button click event
@bot.message_handler(func= lambda m: m.text== "Support 👨🏻‍💻")
def sup(m):
    bot.send_message(chat_id=m.chat.id, text="Send your message to support:")
    bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=m.chat.id)

# Handling the user's first message which is saved in 'Support.text' state
@bot.message_handler(state=Support.text)
def sup_text(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="answer", callback_data=m.from_user.id))
 
    bot.send_message(chat_id=SUPPORT_ID, text=f"Recived a message from ```{m.from_user.id}``` with username @{m.from_user.username}:\nMessage text:\n\n*{escape_special_characters(m.text)}*", reply_markup=markup, parse_mode="MarkdownV2")

    bot.send_message(chat_id=m.chat.id, text="Your message was sent!")

    texts[m.from_user.id] = m.text

    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# Handling the callback query when the 'answer' button is clicked
@bot.callback_query_handler(func= lambda call: True)
def answer(call):
    bot.send_message(chat_id=call.message.chat.id, text=f"Send your answer to ```{call.data}```:", parse_mode="MarkdownV2")

    chat_ids.append(int(call.data))

    bot.set_state(user_id=call.from_user.id, state=Support.respond, chat_id=call.message.chat.id)

# Handling the support agent's reply message which is saved in 'Support.respond' state
@bot.message_handler(state=Support.respond)
def answer_text(m):
    chat_id = chat_ids[-1]

    if chat_id in texts:
        bot.send_message(chat_id=chat_id, text=f"Your message:\n_{escape_special_characters(texts[chat_id])}_\n\nSupport answer:\n*{escape_special_characters(m.text)}*", parse_mode="MarkdownV2")
        bot.send_message(chat_id=m.chat.id, text="Your answer was sent!")

        del texts[chat_id]
        chat_ids.remove(chat_id)
    else:
        bot.send_message(chat_id=m.chat.id, text="Something went wrong. Please try again...")

    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# Starting the bot and adding the state filter as a custom filter
if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling()
