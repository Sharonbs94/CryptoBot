from bot_setup import bot
from core.kafka_producer import fetch_data_from_api_and_send_to_kafka

@bot.message_handler(commands=['graph'])
def graph(message):
    args = message.text.split()[1:]

    if len(args) != 3:
        bot.reply_to(message, "Please provide cryptocurrency, currency, and days. Example: /graph bitcoin usd 30")
        return

    coin, currency, days = args
    chat_id = message.chat.id
    command = message.text.split()[0][1:]

    if not days.isdigit() or int(days) <= 0:
        bot.reply_to(message, "Number of days must be a positive integer.")
        return

    days = int(days)
                                                    
    fetch_data_from_api_and_send_to_kafka(coin, chat_id, command, currency, days)

    bot.reply_to(message, "Your graph request is being processed. You will receive it shortly.")
