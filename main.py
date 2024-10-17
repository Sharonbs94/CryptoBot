from bot_setup import bot
from handlers import help_handler, cryptocurrency_handler, graph_handler, news_handler, setalert_handler, checkprice_handler

def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()