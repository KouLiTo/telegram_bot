import logging
import time
from lxml import html
from urllib import request
import sys
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests


TOKEN = "must_be_your_own"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

b1 = KeyboardButton("USD-UAH")
b2 = KeyboardButton("EUR-UAH")
b3 = KeyboardButton("EUR-USD")
b4 = KeyboardButton("JPY-UAH")
b5 = KeyboardButton("GBP-UAH")
b6 = KeyboardButton("AED-UAH")
b7 = KeyboardButton("/help")
qwerty = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
qwerty.row(b1, b2, b3, b4, b5, b6).insert(b7)


HELP = "I will help you to use me.\nTo call currency rates use buttons for the pairs being compared most often.\n" \
       "Or you can type pairs themselves like 'CHF-UAH' as a message to me.\nTo find information about the weather " \
       "in a certain place please type this place as a massage to me like 'New York'"


async def on_start_up(_):
    print("Bot is running")


@dp.message_handler(commands=["start"])
async def start_point(message: types.Message):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    logging.info(f"{user_id=} {user_fullname=} {time.asctime()}")
    await message.reply(f"Hi, {user_fullname}! Exchange rates and weather information for you.", reply_markup=qwerty)


@dp.message_handler(commands=["help"])
async def start_point(message: types.Message):
    await message.reply(HELP)


@dp.message_handler()
async def cur_rates(message: types.Message):
    count = 0
    currency1 = message.text[:3]
    currency2 = message.text[4:]
    for i in data_:
        if isinstance(i, dict):
            if i["currencyCodeA"] == codesA_B(currency1) and i["currencyCodeB"] == codesA_B(currency2):
                if 'rateBuy' in i.keys():
                    count += 1
                    await message.reply(f"Current rates: {currency1} = {i['rateBuy']} {currency2}")
                elif 'rateCross' in i.keys() and 'rateBuy' not in i.keys():
                    count += 1
                    await message.reply(f"Current rates: {currency1} = {i['rateCross']} {currency2}")
    if count == 0:
        try:
            key = "1550bf27013ad36bb6d6ebfe8c840f9f"
            url = "http://api.openweathermap.org/data/2.5/weather"
            parameters = {
                "q": message.text,
                "appid": key,
                "units": "metric"
            }
            final_info = requests.get(url, params=parameters)
            weather = final_info.json()
            await message.reply(f'<b>{str(weather["name"])}: {weather["main"]["temp"]} °C</b>', parse_mode="html")
        except KeyError:
            await message.reply("Sorry, I can not find any related information")


def read_codes():
    with open(cc_name, "r") as f:
        cur_codes = json.load(f)
        return cur_codes


cc_name = "currency_codes.json"

try:
    cur_codes = read_codes()
except Exception:
    response1 = request.urlopen("https://www.iban.com/currency-codes")
    tree = html.fromstring(response1.read())
    elements = tree.xpath("""/html/body/div/div[2]/div/div/div/div/table/tbody/tr[*]/td[3]""")
    elements_ = tree.xpath("""/html/body/div/div[2]/div/div/div/div/table/tbody/tr[*]/td[4]""")
    with open(cc_name, "w") as f:
        json.dump({k.text: v.text for k, v in zip(elements, elements_)}, f, indent=4)
    cur_codes = read_codes()

cur_codes_formated = {k: int(v) for k, v in cur_codes.items() if isinstance(v, str)}  # creates dict with codes from
                                                                                # data parsed from iban.com

try:
    response = request.urlopen("https://api.monobank.ua/bank/currency")   # sending request to monobank
except Exception:
    print("Error. Too many requests. Try again later")
    sys.exit()
else:
    data_ = eval(response.read().decode())  # getting response from Monobank, it takes upto 10 seconds



def amount_float(arg):
    return float(arg)


def codesA_B(arg):
    for k, v in cur_codes_formated.items():
        if k == arg:
            return v


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up)
