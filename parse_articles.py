import wikipedia
import wikipediaapi
from string import punctuation
import os
import json
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pymorphy2 import MorphAnalyzer


pymorphy2_analyzer_rus = MorphAnalyzer()
pymorphy2_analyzer_ukr = MorphAnalyzer(lang='uk')


def get_article_title(url):
    return url.split('/')[-1]


wiki = wikipediaapi.Wikipedia(
    language='ru',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def get_article_text(url):
    title = get_article_title(url)
    page = wiki.page(
        title=title,
        unquote=True,
    )
    return page.text


def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)


def preprocess(text, lang):
    words = word_tokenize(text.lower())
    lemmata = []
    if lang == 'eng':
        lemmatizer = WordNetLemmatizer()
        stop_words = stopwords.words('english')
        for token in words:
            lemma = lemmatizer.lemmatize(token, get_wordnet_pos(token))
            if lemma not in stop_words and lemma not in punctuation:
                lemmata.append(lemma)
        return lemmata
    if lang == 'rus':
        stop_words = stopwords.words('russian')
        stop_words.extend(['это', 'еще', 'ещё', 'весь'])
        pymorphy2_analyzer = pymorphy2_analyzer_rus
    else:
        stop_words = open('ukrainian.txt', 'r', encoding='utf-8').read().split()
        pymorphy2_analyzer = pymorphy2_analyzer_ukr

    for token in words:
        ana = pymorphy2_analyzer.parse(token)[0]
        if ana.normal_form not in stop_words and ana.normal_form not in punctuation:
            word = ana.normal_form
            lemmata.append(word)

    return lemmata


def inverted_index(docs):
    """
        Compiles inverted index from document collection.
        :param docs: dict[list][str]: dict of tokenized documents, where key is document name and value is tokenized text
        :return: dict: inverted index
    """
    inv_index = {}
    for doc_id, text in docs:
        for word in text:
            if word not in inv_index:
                inv_index[word] = {}
            if doc_id in inv_index[word]:
                inv_index[word][doc_id] += 1
            else:
                inv_index[word][doc_id] = 1
    return inv_index


def create_inverted_index(urls, path):
    docs = []
    for doc_id, url in urls:
        text = get_article_text(url)
        docs.append((doc_id, preprocess(text, 'rus')))

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(inverted_index(docs), file, ensure_ascii=False)


def dump_inv_index():
    urls = list(enumerate(open('ru_links.txt', 'r').read().split()))
    epochs = 50
    for i in range(0, epochs):
        print(i)
        create_inverted_index(urls[i * len(urls)//epochs : (i + 1) * len(urls)//epochs], str(i) + '.txt')


def dump_doc_lens_inv_index():
    urls = list(enumerate(open('ru_links.txt', 'r').read().split()))

    epochs = 70
    for i in range(18, epochs):
        print(i)
        lens = []
        tmp_urls = urls[i * len(urls) // epochs: (i + 1) * len(urls) // epochs]
        create_inverted_index(tmp_urls, str(i) + 'index.txt')

        for url in tmp_urls:
            text = preprocess(get_article_text(url[1]), 'rus')
            lens.append(len(text))

        with open(str(i) + 'lens.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(map(str, lens)))


def merge_inv_index(docs):
    base = json.load(open(docs[0], 'r', encoding='utf-8'))

    for filename in docs[1:]:
        other = json.load(open(filename, 'r', encoding='utf-8'))
        for key in other.keys():
            if key in base:
                base[key] = {**base[key], **other[key]}
            else:
                base[key] = other[key]

    with open('inv_index_rus.txt', 'w', encoding='utf-8') as file:
        json.dump(base, file, ensure_ascii=False)


def merge_doc_lens(docs):
    base = open(docs[0], 'r', encoding='utf-8').read().split()

    for filename in docs[1:]:
        other = open(filename, 'r', encoding='utf-8').read().split()
        base = [*base, *other]

    with open('docs_lens_rus.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(base))


