from math import log
import json
import pickle

k1 = 2.0
b = 0.75

def score_BM25(n, qf, N, dl, avdl):
    """
    Computes Okapi BM25 for a particular document and one word in a query.
    NB: min IDF 0 (use built-in max function)
    :param n: number of docs with a word
    :param qf: raw word frequence in doc
    :param N: number of docs in a collection
    :param dl: doc length (in words)
    :param avdl: average doc length in a collection
    :return: float: BM25 score
    """
    idf = log((N - n + 0.5) / (n + 0.5))
    res = idf * (qf * (k1 + 1)) / (qf + k1 * (1 - b + b * dl / avdl))
    return res


def relevance(query, inv_index, docs_lens, N, avdl):
    '''
    Computes relevance for all the documents that contain words from a query.
    :param query: list: preprocessed query
    :return: dict[doc]: dict of documents (keys) and their relevance (value) for current query
    '''
    res = {}

    for word in query:
        if word not in inv_index:
            continue
        for doc in inv_index[word]:
            if doc not in res:
                res[doc] = 0

    for doc in res:
        dl = docs_lens[doc]
        for word in query:
            if word in inv_index:
                n = len(inv_index[word])
                qf = inv_index[word][doc] if doc in inv_index[word] else 0
            else:
                n = 0
                qf = 0
            res[doc] += score_BM25(n, qf, N, dl, avdl)
    return res

inverted_index_ukr = json.load(open('inverted_index_ukr.txt', 'r', encoding='utf-8-sig'))
docs_lengths_ukr = json.load(open('docs_lengths_ukr.txt', 'r', encoding='utf-8-sig'))
N_ukr = len(docs_lengths_ukr)
avdl_ukr = sum(docs_lengths_ukr.values())/N_ukr

inverted_index_rus = json.load(open('inverted_index_rus.txt', 'r', encoding='utf-8-sig'))
docs_lengths_rus = json.load(open('docs_lengths_rus.txt', 'r', encoding='utf-8-sig'))
N_rus = len(docs_lengths_rus)
avdl_rus = sum(docs_lengths_rus.values())/N_rus

def language_detecting(query):
    x_new_sent = trg.transform([query])
    y_new_pred_sent = model.predict(x_new_sent)
    lang = y_new_pred_sent[0]
    return lang

with open('model_sent.pickle', 'rb') as f:
    model = pickle.load(f)
with open('vectorizer.pickle', 'rb') as f:
    trg = pickle.load(f)