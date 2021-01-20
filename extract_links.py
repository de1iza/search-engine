import requests
from bs4 import BeautifulSoup
import validators


def get_links_list(url):
    r = requests.get(url)
    html_content = r.text
    soup = BeautifulSoup(html_content, 'lxml')

    links = ['https://ru.wikipedia.org/' + a.get('href') for a in soup.find_all('a', href=True)]

    links_processed = []
    start_flag = False

    for elem in links:
        if 'index.php' in elem and start_flag:
            break
        if validators.url(elem) and elem.count(':') == 1 and elem.count('#') == 0:
            links_processed.append(elem)
            start_flag = True

    return links_processed


def dump_links():
    output_file = open('links.txt', 'a')
    sections_urls = open('sections_links1.txt', 'r').read().split()
    for url in sections_urls:
        output_file.write('\n'.join(get_links_list(url)) + '\n')
    output_file.close()


def clean_links():
    file = open('links.txt', 'r')
    out = open('ru_links.txt', 'w')
    links = file.read().split()
    links_processed = []

    for elem in links:
        if validators.url(elem) and elem.count('uselang=ru') == 0 and elem.count('ru.wikipedia.org') == 1:
            links_processed.append(elem)

    out.write('\n'.join(links_processed))
    out.close()


def delete_duplicate_links():
    file = open('ru_links.txt', 'r')
    out = open('ru_links.txt', 'w')
    links = set(file.read().split())

    out.write('\n'.join(list(links)))
    out.close()


delete_duplicate_links()
