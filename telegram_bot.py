import logging
from wordcloud import WordCloud
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from save_data import phase
from save_data import cur_link
from save_data import cur_depth
from save_data import example_link
from save_data import words
from parse import parse
import statistics

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, _: CallbackContext):
    if (not update.message.chat.id in phase):  # весь этот иф в отдельную функцию
        phase[update.message.chat.id] = False
        cur_link[update.message.chat.id] = ''
        cur_depth[update.message.chat.id] = 1
        words[update.message.chat.id] = list()
    update.message.reply_text('You can find out what this bot can do by writing /help')


def ask_depth(update: Update, _: CallbackContext):
    if check_start(update):
        return
    update.message.reply_text('Enter the search depth')
    phase[update.message.chat.id] = 'wait_for_depth'


def ask_link(update: Update, _: CallbackContext):
    if check_start(update):
        return
    update.message.reply_text('Enter a link to the article you are interested in')
    phase[update.message.chat.id] = 'wait_for_link'


def check_start(update: Update):
    if not update.message.chat.id in phase:
        update.message.reply_text('Use /start to use this bot.')
        return True
    return False


def help_command(update: Update, _: CallbackContext):
    update.message.reply_text('Use /start to start using this bot. \n' +
                              'Use /enter_link to enter a link to the article you are interested in\n' +
                              'Use /enter_depth to enter the search depth\n' +
                              'Use /describe to get statistics on the article\n' +
                              'Use /describe \" word \" to get statistics on the word\n' +
                              'Use /world_cloud #\"color\" to get a cloud of words, where the color is a 16 bit number of length 6. For example /world_cloud #AAAAAA\n' +
                              'Use /top n asc/desc to get a list of the most frequently/rarely used words\n' +
                              'Use /stop_words to get a list of outlier words')


def message_handler(update: Update, _: CallbackContext):
    if check_start(update):
        return
    if phase[update.message.chat.id] == 'wait_for_depth':
        if not update.message.text.isdigit():
            update.message.reply_text('Enter valid depth')
            return
        cur_depth[update.message.chat.id] = int(update.message.text)
        phase[update.message.chat.id] = 'wait_for_link'
    elif phase[update.message.chat.id] == 'wait_for_link':
        if update.message.text.find(example_link) == -1:
            update.message.reply_text('Enter valid link')
            return
        words[update.message.chat.id].clear()
        cur_link[update.message.chat.id] = update.message.text
        try:
            parse(update.message.text, update.message.chat.id, cur_depth[update.message.chat.id])
            phase[update.message.chat.id] = 'Working'
        except:
            update.message.reply_text('Reduce the search depth')


def top(update: Update, context: CallbackContext):
    if check_work(update):
        return
    text = context.args
    if len(text) != 2 or (text[1] != 'asc' and text[1] != 'desc') or not text[0].isdigit():
        update.message.reply_text('Use /help')
        return
    n = int(text[0])
    asc = True
    if text[1] == 'desc':
        asc = False
    words = statistics.top(update.message.chat.id, n, asc)
    for word in words:
        update.message.reply_text(word)


def stop_words(update: Update, _: CallbackContext):
    if check_work(update):
        return
    words = statistics.stop_words(update.message.chat.id)
    for word in words:
        update.message.reply_text(word)


def describe(update: Update, context: CallbackContext):
    if check_work(update):
        return
    if not context.args:
        words1, words2 = statistics.describe(update.message.chat.id)
        cnt_calls = 0
        words_list = ['']
        ptr = 0
        for cnt in words1:
            if len(words_list[ptr]) + 200 > 4096:
                ptr += 1
                words_list.append('')
            words_list[ptr] += 'Слов, которые встречаются ' + str(cnt[0]) + ' раз: ' + str(cnt[1]) + "\n"
        for word in words_list:
            update.message.reply_text(word)
        words_list = ['']
        ptr = 0
        for cnt in words2:
            if len(words_list[ptr]) + 200 > 4096:
                ptr += 1
                words_list.append('')
            words_list[ptr] += 'Слов, длины ' + str(cnt[0]) + ': ' + str(cnt[1]) + "\n"
        for word in words_list:
            update.message.reply_text(word)
    else:
        text = context.args
        if len(text) != 1:
            update.message.reply_text('Use /help')
            return
        cnt_in_text, cnt_of_inclusion = statistics.describe_word(update.message.chat.id, text[0])
        if cnt_in_text == -1:
            update.message.reply_text('Слово не встречается в тексте')
            return
        update.message.reply_text('Слово встречается в тексте ' + str(cnt_in_text) + ' раз\n' +
                                  'Слово встречается в тексте чаще, чем ' + str(cnt_of_inclusion) + ' других слов')


def world_cloud(update: Update, context: CallbackContext):
    if check_work(update):
        return
    text = context.args
    if len(text) != 1:
        update.message.reply_text('Use /help')
        return
    words_in_cloud = ' '.join(words[update.message.chat.id])
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color=text[0]).generate(words_in_cloud)
    wordcloud.to_file('cloud.png')
    file = open('cloud.png', 'rb')
    context.bot.send_photo(update.message.chat.id, file)


def check_work(update: Update):
    if check_start(update):
        return True
    if phase[update.message.chat.id] != 'Working':
        update.message.reply_text('Use /help')
        return True
    return False


def run_bot():
    updater = Updater('YOUR_TOKEN')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('enter_depth', ask_depth))
    dp.add_handler(CommandHandler('enter_link', ask_link))
    dp.add_handler(CommandHandler('top', top))
    dp.add_handler(CommandHandler('stop_words', stop_words))
    dp.add_handler(CommandHandler('describe', describe))
    dp.add_handler(CommandHandler('world_cloud', world_cloud))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    updater.start_polling()
    updater.idle()
