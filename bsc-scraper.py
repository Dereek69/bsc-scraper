import requests
import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import lxml.html
import logging
from lxml import etree
import pickle
import os

url = "https://bscscan.com/tokentxns"
telegram_token = ""
token_list = dict()

def start_command(update,context):
    """Send a message when the command /start is issued."""
    print("start")
    update.message.reply_text('Welcome to this bot\nFollow me on twitter @Dereek70')

def check(context: telegram.ext.CallbackContext):
    global token_list
    try:
        page = requests.get(url, stream = True, timeout = 5)
    except (
        requests.ConnectionError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectTimeout,
    ) as e:
        print(e)
    print(page)
    page.raw.decode_content = True
    tree = lxml.html.parse(page.raw)
    tr_list = tree.xpath("/html/body/div[1]/main/div[2]/div/div/div[2]/table/tbody/tr")
    #print(tr_list)
    for tr in tr_list:
        a = tr.xpath("td[9]/a")[0]
        token = a.get('href')
        #print(token)
        if token in token_list:
            print("already in list")
        else:
            print("new token found")
            token_list[token] = True
            name,ticker,supply,holders = get_data(token)
            context.bot.send_message(chat_id = "@BscNewTokens", text = "NEW TOKEN FOUND\n\n" + "Name: " + name + "\nTicker: " + ticker + "\nSupply: " + supply + "\nHolders: " + holders + "\n\nhttps://bscscan.com" + token)
            

def get_data(token):
    try:
        page = requests.get("https://bscscan.com" + token, stream = True, timeout = 5)
    except (
        requests.ConnectionError,
        requests.exceptions.ReadTimeout,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectTimeout,
    ) as e:
        print(e)

    page.raw.decode_content = True
    tree = lxml.html.parse(page.raw)

    name = tree.xpath("/html/body/div[1]/main/div[1]/div/div[1]/h1/div/span")[0].text_content()
    ticker = tree.xpath("/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[2]/div[2]/b")[0].text_content()
    supply = tree.xpath("/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[2]/div[2]/span[1]")[0].text_content()
    holders = tree.xpath("/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div")[0].text_content()

    print(name)
    print(ticker)
    print(supply)
    print(holders)

    return name,ticker,supply,holders

def backup(context: telegram.ext.CallbackContext):
    print('saving backup')

    with open('backup.txt','wb') as f:
        pickle.dump(token_list,f)
    print("saved backup of\n")
    print(token_list)


def main():
    global token_list
    if os.path.getsize('backup.txt') > 0: 
        with open('backup.txt','rb') as f:
            unpickler = pickle.Unpickler(f)
            token_list = unpickler.load()

    updater = Updater(token = telegram_token, use_context = True)
    j = updater.job_queue

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start",start_command))
    j.run_repeating(check,interval = 5, first = 0)
    j.run_repeating(backup,interval = 60, first= 20)

    updater.start_polling()

if __name__ == '__main__':
    main()
