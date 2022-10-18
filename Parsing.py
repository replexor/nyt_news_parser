from python_translator import Translator
from telegram.ext import CallbackContext
from telegram import Update
from bs4 import BeautifulSoup
import cfscrape
import time
from State import State


def getPageData():
    siteUrl = 'https://www.nytimes.com'
    scraper = cfscrape.CloudflareScraper()

    html = None
    soup = None

    try:
        html = str(scraper.get(siteUrl + '/section/world/europe').content)
        soup = BeautifulSoup(html, 'lxml')
        return [soup, siteUrl]
    except:
        return ['', siteUrl]


def parseNews(dataOfPage, num):
    if dataOfPage[0] == '' or not (num >= 0 and num < 10): return [] # num - костыль!
    
    article = dataOfPage[0].select('.css-1l4spti')[num].a

    return [
        translateText(validText(article.find('h2', 'css-1kv6qi e15t083i0'))),
        translateText(validText(article.find('p', 'css-1pga48a e15t083i1'))),
        translateText(validText(article.find('span', 'css-1n7hynb'))),
        dataOfPage[1] + article['href']
    ]


# Предполагает выполнение в другом потоке с регулировкой бесконечного цикла
def loadToTelegram(update: Update, context: CallbackContext):
    NUM_OF_ARTICLES = 10
    localArticles = [] # Последние 10 сохранённых записей
    newArticles = [] # Новые записи, ожидающие отправки и внесения в localArticles
    dataOfPage = [] # Хранит объект страницы BeautifulSoup для парсинга, а также главный URL сайта
    dataOfArticle = [] # Содержит текстовые данные для отправки в Telegram по каждой записи
    outText = '' # Переменная для конкатенации текста для последующей отправки данных в Telegram

    while State.treadStop == False:
        dataOfPage = getPageData()

        if len(localArticles) != NUM_OF_ARTICLES:
            # Сохранение последних 10 записей 
            for i in range(len(localArticles), NUM_OF_ARTICLES):
                localArticles.insert(0, parseNews(dataOfPage, i))
        else:
            # Сравнение обновлённых записей с сохранёнными
            for i in range(len(localArticles)):
                dataOfArticle = parseNews(dataOfPage, i)

                # Условие проверки наличия новых записей
                # Если самая новая сохранённая запись равна самой новой обновлённой,
                # новых записей больше нет, цикл больше не требуется
                if localArticles[len(localArticles) - 1][3] == dataOfArticle[3]: 
                    break
                else:
                    newArticles.insert(0, dataOfArticle.copy())

                dataOfArticle.clear()

        # Формирование поста и отправка в Telegram
        for i in range(len(newArticles)):
            # Удаляет самую старую запись *** добавляет в конец самую старую из обновлённых
            del(localArticles[0])
            localArticles.append(newArticles[i])

            outText = str(newArticles[i][0]) + '\n\n'
            outText += str(newArticles[i][1]) + ' (' + str(newArticles[i][2]) + ')\n\n'
            outText += str(newArticles[i][3])

            context.bot.sendMessage(chat_id=update.effective_chat.id, text=outText)
        
        newArticles.clear()
        dataOfPage.clear()

        time.sleep(60)


def translateText(text):
    translator = Translator()

    try:
        return translator.translate(str(text), 'ru', 'en')
    except:
        return text


def validText(text):
    if text == None:
        return ""
    else:
        return str(text.contents[0])