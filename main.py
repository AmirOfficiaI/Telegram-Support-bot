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

# Import data from config.py file
from config import BOT_TOKEN, SUPPORT_ID

# Creating an instance of StateMemoryStorage
state_storage = StateMemoryStorage()

# Creating a TeleBot object with API key and state storage
bot = telebot.TeleBot(token=BOT_TOKEN, state_storage=state_storage)

# Declaring two global lists to keep track of chat ids and texts
chat_ids = []
texts = {}

# Creating a state group 'Support' with two states 'text' and 'respond'
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
    # Creating a reply keyboard markup with a button 'پشتیبانی'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Support 👨🏻‍💻")
    # Sending a message with the reply keyboard markup
    bot.send_message(chat_id=m.chat.id, text=f"Hello *{m.from_user.first_name}*", reply_markup=markup, parse_mode="MarkdownV2")

# Handling the 'Support 👨🏻‍💻' button click event
@bot.message_handler(func= lambda m: m.text== "Support 👨🏻‍💻")
def sup(m):
    # Sending a message to the user to send their message
    bot.send_message(chat_id=m.chat.id, text="Send your message to support:")
    # Setting the state to 'Support.text'
    bot.set_state(user_id=m.from_user.id, state=Support.text, chat_id=m.chat.id)

# Handling the user's first message which is saved in 'Support.text' state
@bot.message_handler(state=Support.text)
def sup_text(m):
    # Creating an inline keyboard markup with a button 'answer'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="answer", callback_data=m.from_user.id))
    # Sending the message with the user's message and the inline keyboard markup
    bot.send_message(chat_id=SUPPORT_ID, text=f"Recived a message from ```{m.from_user.id}``` with username @{m.from_user.username}:\nMessage text:\n\n*{escape_special_characters(m.text)}*", reply_markup=markup, parse_mode="MarkdownV2")
    # Sending a confirmation message to the user
    bot.send_message(chat_id=m.chat.id, text="Your message was sent!")
    # Saving the user's message in the 'texts' dictionary with their user id as the key
    texts[m.from_user.id] = m.text
    # Deleting the state from the 'Support.text' state group
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# Handling the callback query when the 'answer' button is clicked
@bot.callback_query_handler(func= lambda call: True)
def answer(call):
    # Sending a message with instructions for the support agent to reply
    bot.send_message(chat_id=call.message.chat.id, text=f"Send your answer to ```{call.data}```:", parse_mode="MarkdownV2")
    # Adding the user's id to the 'chat_ids' list
    chat_ids.append(int(call.data))
    # Setting the state to 'Support.respond'
    bot.set_state(user_id=call.from_user.id, state=Support.respond, chat_id=call.message.chat.id)

# Handling the support agent's reply message which is saved in 'Support.respond' state
@bot.message_handler(state=Support.respond)
def answer_text(m):
    # Retrieving the user's id from the 'chat_ids' list
    chat_id = chat_ids[-1]
    # Checking if the user's id exists in the 'texts' dictionary
    if chat_id in texts:
        # Sending a formatted message to the user with their original message and the support agent's reply
        bot.send_message(chat_id=chat_id, text=f"Your message:\n_{escape_special_characters(texts[chat_id])}_\n\nSupport answer:\n*{escape_special_characters(m.text)}*", parse_mode="MarkdownV2")
        # Sending a confirmation message to the support agent that their message has been sent
        bot.send_message(chat_id=m.chat.id, text="Your answer was sent!")
        # Removing the user's id and text from the global lists
        del texts[chat_id]
        chat_ids.remove(chat_id)
    else:
        # In case of an error, sending an error message to the support agent
        bot.send_message(chat_id=m.chat.id, text="Something went wrong. Please try again...")
    # Deleting the state from the 'Support.respond' state group
    bot.delete_state(user_id=m.from_user.id, chat_id=m.chat.id)

# Starting the bot and adding the state filter as a custom filter
if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling()
