from bot_setup import bot
from core.kafka_producer import fetch_data_from_api_and_send_to_kafka

@bot.message_handler(commands=['news'])
def news(message):
    args = message.text.split()[1:]

    if len(args) != 1:
        bot.reply_to(message, "Please provide a cryptocurrency. Example: /news bitcoin")
        return

    coin = args[0]
    chat_id = message.chat.id
    command = message.text.split()[0][1:]

    fetch_data_from_api_and_send_to_kafka(coin, chat_id, command)

    bot.reply_to(message, "Your news request is being processed. You will receive it shortly.")
