from bot_setup import bot

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Here are the available commands:\n"
                          "/cryptocurrency: Check cryptocurrency price.\n"
                          "Usage: /cryptocurrency [cryptocurrency] [currency]\n"
                          "Example: /cryptocurrency bitcoin usd\n"
                          "\n"
                          "/graph: Check cryptocurrency price over a specified number of days.\n"
                          "Usage: /graph [cryptocurrency] [currency] [days]\n"
                          "Example: /graph bitcoin usd 30\n"
                          "\n"
                          "/news: Get top-rated cryptocurrency news.\n"
                          "Usage: /news [cryptocurrency]\n"
                          "Example: /news bitcoin\n"
                          "\n"
                          "/setalert: Set a price alert for a cryptocurrency.\n"
                          "Usage: /setalert [cryptocurrency] [currency] [condition: above/below] [target price]\n"
                          "Example: /setalert bitcoin usd above 50000")
