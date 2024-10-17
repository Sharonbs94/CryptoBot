from config import api_urls
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.collections import LineCollection
import numpy as np
import os
import requests
import io
import json


def format_currency(price):
    return '{:,.2f}'.format(price)


def currency_symbols(currency_code):
    convert_symbols = {'ils': '₪', 'eur': '€', 'usd': '$', 'jpy': '¥'}
    return convert_symbols.get(currency_code.lower(), currency_code.upper())


def send_to_telegram_cryptocurrency(coin, currency, price, chat_id):
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    format_price = format_currency(price)
    format_currency_symbol = currency_symbols(currency)
    message = f'{coin.capitalize()} price in {currency.upper()}: {format_currency_symbol}{format_price}'
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to send message to Telegram. Status code: {response.status_code}, Chat ID: {chat_id}")


def send_to_telegram_graph(data, chat_id, coin, currency, days):
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"

    if isinstance(data, str):
        data = json.loads(data)

    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df['price_change'] = df['price'].diff()
    df['up'] = df['price_change'] >= 0

    points = np.array([mdates.date2num(df['timestamp']), df['price']]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    colors = ['green' if up else 'red' for up in df['up'][1:]]

    lc = LineCollection(segments, colors=colors, linewidths=2)

    plt.style.use('seaborn-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.add_collection(lc)

    ax.set_xlim(df['timestamp'].min(), df['timestamp'].max())
    ax.set_ylim(df['price'].min() * 0.98, df['price'].max() * 1.02)

    ax.set_title(f'{coin.capitalize()} Price Over Last {days} Days in {currency.upper()}', fontsize=16, pad=20)
    ax.set_xlabel('Date', fontsize=14, labelpad=15)
    ax.set_ylabel(f'Price in {currency.upper()}', fontsize=14, labelpad=15)

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')

    def y_fmt(x, pos):
        return '{:,.2f}'.format(x)
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    max_price = df['price'].max()
    max_date = df.loc[df['price'].idxmax(), 'timestamp']
    min_price = df['price'].min()
    min_date = df.loc[df['price'].idxmin(), 'timestamp']
    avg_price = df['price'].mean()

    ax.plot(max_date, max_price, marker='o', color='darkblue', markersize=8, label='Highest')
    ax.plot(min_date, min_price, marker='o', color='darkorange', markersize=8, label='Lowest')

    ax.legend(loc='upper left')

    plt.tight_layout()

    image_path = 'graph.png'
    plt.savefig(image_path, dpi=400)
    plt.close()

    with open(image_path, 'rb') as image_file:
        files = {'photo': image_file}
        data = {'chat_id': chat_id}
        response = requests.post(url, data=data, files=files)

    if response.status_code != 200:
        print(f"Failed to send image to Telegram. Status code: {response.status_code}, Chat ID: {chat_id}")

    currency_symbol = currency_symbols(currency)

    opening_price = df.iloc[0]['price']
    closing_price = df.iloc[-1]['price']
    price_change = closing_price - opening_price
    percentage_change = (price_change / opening_price) * 100 if opening_price != 0 else 0
    trend = "increased" if price_change > 0 else "decreased" if price_change < 0 else "not changed"
    trend_symbol = '🟢' if price_change > 0 else '🔴' if price_change < 0 else '⚪'

    message = (
        f"{coin.capitalize()} Price Summary Over Last {days} Days in {currency.upper()}:\n"
        f"Opening Price: {currency_symbol}{opening_price:,.2f}\n"
        f"Closing Price: {currency_symbol}{closing_price:,.2f}\n"
        f"Highest Price: {currency_symbol}{max_price:,.2f} on date: {max_date.strftime('%Y-%m-%d')}\n"
        f"Lowest Price: {currency_symbol}{min_price:,.2f} on date: {min_date.strftime('%Y-%m-%d')}\n"
        f"Average Price: {currency_symbol}{avg_price:,.2f}\n"
        f"Price has {trend} by {currency_symbol}{abs(price_change):,.2f} "
        f"({percentage_change:+.2f}% {trend_symbol}) over the last {days} days."
    )
    
    message_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(message_url, params=params)
    if response.status_code != 200:
        print(f"Failed to send summary message to Telegram. Status code: {response.status_code}, Chat ID: {chat_id}")


def send_to_telegram_news(data, chat_id, coin):
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    message_text = f"📰 *Latest News about {coin.capitalize()}*:\n\n"
    max_articles = 5  

    try:
        df = pd.json_normalize(data['results'])
        
        if 'votes.liked' not in df.columns:
            df['votes.liked'] = 0
        else:
            df['votes.liked'] = pd.to_numeric(df['votes.liked'], errors='coerce').fillna(0).astype(int)
        
        df['currencies'] = df['currencies'].fillna('').astype(str)
        df_coin = df[df['currencies'].str.contains(coin, case=False, na=False)]
        
        if df_coin.empty:
            message_text += "No news articles found for this cryptocurrency."
        else:
            df_coin = df_coin.sort_values(by='votes.liked', ascending=False)
            result_df = df_coin[['title', 'url']]
            articles_to_send = result_df.head(max_articles)
            for index, row in articles_to_send.iterrows():
                title = row['title'].replace('_', '\\_').replace('*', '\\*').replace('[', '\\[')
                message_text += f"*{title}* \n[Read more]({row['url']})\n\n"
    except Exception as e:
        print(f"Error processing news data: {e}")
        message_text += "No news found or an error occurred while processing the news data."

    params = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'Markdown'
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to send news message to Telegram. Status code: {response.status_code}, Chat ID: {chat_id}")


def command_url(command):
    urls = {'cryptocurrency':api_urls.COINGECKO_PRICE_URL, 
                'graph':api_urls.COINGECKO_PRICE_GRAPH_URL, 
                'news':api_urls.CRYPTOPANIC_NEWS_URL}
    return urls.get(command)