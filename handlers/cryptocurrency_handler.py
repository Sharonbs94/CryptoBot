from bot_setup import bot
from core.kafka_producer import fetch_data_from_api_and_send_to_kafka

@bot.message_handler(commands=['cryptocurrency'])
def cryptocurrency(message):
    args = message.text.split()[1:]

    if len(args) != 2:
        bot.reply_to(message, "Please provide both cryptocurrency and currency. Example: /cryptocurrency bitcoin usd")
        return

    coin, currency = args
    chat_id = message.chat.id
    command = message.text.split()[0][1:]

    fetch_data_from_api_and_send_to_kafka(coin, chat_id, command, currency)

    bot.reply_to(message, "Your request is being processed. You will receive the price shortly.")