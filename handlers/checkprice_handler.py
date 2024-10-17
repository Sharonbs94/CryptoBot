from bot_setup import bot
from config import api_urls
from utils.shared_data import user_target_lst
from utils.functions import format_currency, currency_symbols
import requests
import time

def check_price_alerts():
    url = api_urls.COINGECKO_PRICE_URL
    
    while True:
        if user_target_lst:
            for alert in user_target_lst:
                params = {
                    'ids': alert['ids'],
                    'vs_currencies': alert['vs_currencies']
                }

                try:
                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        
                        current_price = data.get(alert['ids'], {}).get(alert['vs_currencies'])
                        if current_price is None:
                            continue

                        formatted_price = format_currency(current_price)
                        formatted_target_price = format_currency(alert['price_target'])
                        currency_symbol = currency_symbols(alert['vs_currencies'])

                        if alert['condition'] == 'above' and current_price > alert['price_target']:
                            message = f"{alert['ids'].capitalize()} price is above {currency_symbol}{formatted_target_price} {alert['vs_currencies']}.\nCurrent price: {currency_symbol}{formatted_price}"
                            bot.send_message(alert['chat_id'], message)
                            user_target_lst.remove(alert)
                        elif alert['condition'] == 'below' and current_price < alert['price_target']:
                            message = f"{alert['ids'].capitalize()} price is below {currency_symbol}{formatted_target_price} {alert['vs_currencies']}.\nCurrent price: {currency_symbol}{formatted_price}"
                            bot.send_message(alert['chat_id'], message)
                            user_target_lst.remove(alert)

                except Exception as e:
                    pass

        time.sleep(30)