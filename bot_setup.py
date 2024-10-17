import telebot
from config import api_tokens

def create_bot():
    bot = telebot.TeleBot(api_tokens.TELEBOT_TOKEN)
    return bot

bot = create_bot()