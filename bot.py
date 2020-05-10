from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup
import googlesearch
import requests
import pyowm
import wikipedia


class Bot:
    def __init__(self):
        self.main()

    def find(self, update, context):
        words = update.message.text.lstrip('/find ')

        if words:
            url = 'https://www.google.ru/search?q=' + '_'.join(words.split())
            url1 = ''

            for que in googlesearch.search(words, lang='ru', start=0, stop=1):
                url1 += que + '\n'

            update.message.reply_text(url1 + '\n\nА вот все сайты под запрос.\n\n' + url)
        else:
            update.message.reply_text('Вы ничего не ввели :^(')

    def wiki_random(self, update, context):
        url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%'\
              'D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%'\
              'D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0'

        update.message.reply_text(url)

    def start(self, update, context):
        update.message.reply_text(
            "Привет! Я бот, который помогает искать информацию в интернете.\n"
            "Напиши /help для списка команд.")

    def help(self, update, context):
        update.message.reply_text(
            "Что ж, все-таки мне нужно работать: вы не закрыли меня сразу\n\n"
            "Вот Список команд, которые я могу выполнить(только попробуй введи одну из них!)\n\n"
            "/find ЗАПРОС Выдает ссылку на первый сайт в гугле по запросу.\n"
            "/wiki ЗАПРОС Выдает 2 предложения из википедии по запросу\n"
            "/wiki_random Если не знаешь, что спросить у википедии.\n"
            "/weather ГОРОД Выдает текущую погоду в городе и совет как одеться.\n"
            "/dog Случайная картинка собачки.\n"
            "/cat Случайная картинка котика.\n\n"
            "Ну вот и все получается.")

    def cat(self, update, context):
        r = requests.get('https://api.thecatapi.com/v1/images/search')

        url = (str(r.text).split('url":"'))[1].split('"')[0]

        update.message.reply_photo(url)

    def dog(self, update, context):
        r = requests.get('https://dog.ceo/api/breeds/image/random')

        url = str(r.text).split('":"')[1].split('",')[0]
        url = (url.lstrip('https:\/\/')).replace('\\', '/')

        update.message.reply_photo(url)

    def check_weather(self, city):
        try:
            owm = pyowm.OWM('cc4b2680d5c584475e0edcf259c3a832', language='ru')

            observation = owm.weather_at_place(city)

            w = observation.get_weather()
            temp = w.get_temperature('celsius')['temp']

            return w.get_detailed_status(), temp
        except pyowm.exceptions.api_response_error.NotFoundError:
            return None

    def weather(self, update, context):
        city = update.message.text.lstrip('/weather ')

        if self.check_weather(city):
            w_det, temp = self.check_weather(city)

            reply = 'В городе ' + city + ' сейчас ' + w_det

            reply += ', температура ' + str(round(temp)) + ' градусов.' + '\n\n'

            if 'дождь' in reply:
                reply += 'На улицу лучше не выходить.'
            elif temp < 0:
                reply += 'Оденься в зимнее.'
            elif temp < 18:
                reply += 'Прохладно, надень кофту.'
            elif temp < 25:
                reply += 'Тепло, надевай что хочешь.'
            else:
                reply += 'Жарко, надень головной убор.'

            update.message.reply_text(reply)
        else:
            update.message.reply_text('Город введен некорректно или его не существует.')

    def wiki(self, update, context):
        wikipedia.set_lang('ru')

        msg = update.message.text.lstrip('/wiki ')
        data = wikipedia.summary(msg, sentences=2)

        update.message.reply_text(data)

    def on_message(self, update, context):
        keywords = ['что', 'когда', 'где', 'почему', 'зачем']

        if 'прив' in update.message.text.lower():

            reply_keyboard = [['Хорошо'], ['Не очень']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

            update.message.reply_text('Привет, как дела?', reply_markup=markup)
            return

        if 'хорошо' == update.message.text.lower():
            update.message.reply_text('Это хорошо, что все хорошо')
            return

        if 'не очень' == update.message.text.lower():
            update.message.reply_text('Что ж, плохо, что все плохо')
            return

        for el in keywords:
            if el in update.message.text.lower():
                update.message.reply_text('Сам гадаю.')
                return

        update.message.reply_text('Бип-боп ай эм робот, я вас не понимаю.')

    def main(self):
        REQUEST_KWARGS = {
            'proxy_url': 'socks5://47.90.74.82:29988',
        }

        updater = Updater('1293277966:AAFGmmNzWt3qnuBYLCKk-eBUvpjaKeTK_lQ',
                          use_context=True,
                          request_kwargs=REQUEST_KWARGS)

        dp = updater.dispatcher

        dp.add_handler(CommandHandler('find', self.find))
        dp.add_handler(CommandHandler('wiki_random', self.wiki_random))
        dp.add_handler(CommandHandler('start', self.start))
        dp.add_handler(CommandHandler('help', self.help))
        dp.add_handler(CommandHandler('cat', self.cat))
        dp.add_handler(CommandHandler('dog', self.dog))
        dp.add_handler(CommandHandler('weather', self.weather))
        dp.add_handler(CommandHandler('wiki', self.wiki))
        dp.add_handler(MessageHandler(Filters.all, self.on_message))

        updater.start_polling()

        updater.idle()


if __name__ == '__main__':
    bot = Bot()
