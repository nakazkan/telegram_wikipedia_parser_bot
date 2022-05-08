import requests
from bs4 import BeautifulSoup
import re
from save_data import words


def remove_text_between_parens(text):
    n = 1
    while n:
        text, n = re.subn(r'\{[^{}]*\}', ' ', text)
    return text


def get_html(url):
    r = requests.get(url).text
    return r


def get_soup(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    return soup


def parse(url, id, cnt):
    links = list()
    links.append(url)
    internal_links = {url: 1}
    for reference in links:
        soup = get_soup(reference)
        label_p = soup.find_all('p')
        for items in label_p:
            label_a = items.find_all('a')
            for j in label_a:
                link = j.get('href')
                if link == None or internal_links[reference] == cnt:
                    continue
                if link.find('.wikipedia.') != -1 and link not in internal_links:
                    links.append(link)
                    internal_links[link] = internal_links[reference] + 1
                elif link.find('/wiki/') != -1 and 'https://ru.wikipedia.org' + link not in internal_links:
                    links.append('https://ru.wikipedia.org' + link)
                    internal_links['https://ru.wikipedia.org' + link] = internal_links[reference] + 1

    for link in links:
        soup = get_soup(link)
        label = soup.find_all('div', class_='mw-parser-output')
        strings = list()
        for items in label:
            main_text = items.find_all('p')
            for string in main_text:
                strings.append(string.text)
            main_text = items.find_all('li')
            for string in main_text:
                strings.append(string.text)
        for string in strings:
            new_str = re.sub(r'\[[^\]]+\]', ' ', string)
            new_str = remove_text_between_parens(new_str)
            new_str = new_str.lower()
            new_str_divided = new_str.split('\u0301')
            new_str = ''
            for i in new_str_divided:
                new_str += i
            new_str = re.sub(r'\.', ' ', new_str)
            new_str = re.sub(r'[^а-яёa-z-0-9]', ' ', new_str)
            new_str = new_str.split()
            for word in new_str:
                words[id].append(word)
