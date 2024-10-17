from bot_setup import bot
from config import api_urls
from utils.functions import format_currency, currency_symbols
import requests

@bot.message_handler(commands=['setalert'])
def setalert(message):
    url = api_urls.COINGECKO_PRICE_URL
    args = message.text.split()[1:]
    if len(args) != 4:
        bot.reply_to(message, "Please provide cryptocurrency, currency, condition: above/below and target price.")
        return

    coin, currency, condition, target_price = args
    target_price = float(target_price)

    params = {
        'ids': coin,
        'vs_currencies': currency
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if coin in data and currency in data[coin]:
            price = data[coin][currency]
            formatted_price = format_currency(price)
            formatted_target_price = format_currency(target_price)
            currency_symbol = currency_symbols(currency)

            if condition == 'above' and target_price > price:
                bot.reply_to(message, f'{coin.capitalize()} target is set to: {currency_symbol}{formatted_target_price}\nCurrent {coin.capitalize()} price: {currency_symbol}{formatted_price}')
            elif condition == 'below' and target_price < price:
                bot.reply_to(message, f'{coin.capitalize()} target is set to: {currency_symbol}{formatted_target_price}\nCurrent {coin.capitalize()} price: {currency_symbol}{formatted_price}')
            else:
                bot.reply_to(message, f'Wrong target, cryptocurrency price is already: {price}')
        else:
            bot.reply_to(message, f'Invalid coin or currency.')
    else:
        bot.reply_to(message, f'Error: {response.status_code}')