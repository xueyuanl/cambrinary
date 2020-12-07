#!/usr/bin/env python3
import argparse
import asyncio
from argparse import RawTextHelpFormatter

import aiohttp
from bs4 import BeautifulSoup

from .type import *


def get_args():
    parser = argparse.ArgumentParser(description='A linux online terminal dictionary based on cambridge dictionary',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-w', '--word', required=True, nargs='+', action='store', help='the word you want to look up')
    parser.add_argument('-t', '--translation', action='store',
                        help="Prefered language to explain. Defult(english explaination)\n"
                             "Supported language:\n"
                             "{}".format(''.join(['- ' + lang + '\n' for lang in SUPPORT_LANG])))
    parser.add_argument('-s', '--synonym', action="store_true", help='show the synonym of the word if has')
    args = parser.parse_args()
    return args


async def load(word, trans):
    url = 'https://dictionary.cambridge.org/dictionary/' + trans + '/' + word
    cmd = 'curl -k -X GET {}'.format(url)
    process = await asyncio.subprocess.create_subprocess_shell(cmd, shell=True, stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error('failed to {}'.format(cmd))
        logger.error('subprocess stderr: {}'.format(stderr.decode("utf-8").strip()))
    else:
        logger.info('successfully execute: {}'.format(cmd))
        return stdout.decode('utf-8').strip()

    # the aio method is temporally dropped, since it hit an error:
    # ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:852)
    # async with aiohttp.request('GET', url) as resp:
    #     html = await resp.text()
    #     return html

    # from urllib import request
    # response = request.urlopen(url)
    # html = response.read()
    # return html


def get_part_speeches(dict, trans):
    """
    'help' has verb and noun at the same time. So each of them for one part of speech(pos)
    :param dict: dictionary
    :param trans: translation language
    :return: a list of pos
    """
    if trans == GB or trans == CN:
        return dict.findAll('div', attrs={'class': 'pr entry-body__el'}) or \
               dict.findAll('div', attrs={'class': 'entry-body__el clrd js-share-holder'})
    elif trans == DE:
        return dict.findAll('div', attrs={'class': 'd pr di english-german kdic'})
    elif trans == JP or trans == KR:
        return dict.findAll('div', attrs={'class': 'pr entry-body__el'})
    elif trans == FR:
        return dict.findAll('div', attrs={'class': 'd pr di english-french kdic'})
    elif trans == IT:
        return dict.findAll('div', attrs={'class': 'pr entry-body__el'}) or \
               dict.findAll('div', attrs={
                   'class': 'di $dict entry-body__el entry-body__el--smalltop clrd js-share-holder'})  # for look-up case
    elif trans == RU:
        return dict.findAll('div', attrs={'class': 'di $ entry-body__el entry-body__el--smalltop clrd js-share-holder'})


def get_dictionary(html):
    """
    retrieve dictionary body.
    :param html:
    :return:
    """
    pr_dictionary = 'pr dictionary'
    entry_body = 'entry-body'
    parsed_html = BeautifulSoup(html, features='html.parser')
    # this area contains all the dictionaries
    res_dict = None
    dictionaries = parsed_html.body.findAll('div', attrs={'class': pr_dictionary})
    if dictionaries:  # get at least one dictionary

        res_dict = dictionaries[0]
        logger.info('get a dictionary by {}'.format(pr_dictionary))
    else:  # no dictionary, just entry-body
        res_dict = parsed_html.body.find('div', attrs={'class': entry_body})
        logger.info('get a dictionary by {}'.format(entry_body))
    return res_dict


async def look_up(word, trans, synonym, results):
    logger.info('begin to retrieve word: [{}] in {}'.format(word, trans))
    html = await load(word, TRANSLATION[trans])
    dictionary = get_dictionary(html)
    if not dictionary:
        results[word] = 'No result for {}'.format(word)
        logger.info('No result for {}'.format(word))
        return

    part_speeches = get_part_speeches(dictionary, trans)
    logger.info('the number of part_speeh is {}'.format(len(part_speeches) if part_speeches else 0))
    Word.trans = trans
    Word.synonym = synonym
    word_obj = Word()
    word_obj.parse_part_speeches(part_speeches)
    results[word] = word_obj.to_str()
    if not results[word]:
        logger.error('word {} has no result'.format(word))


def main():
    args = get_args()
    trans = conf.default_trans_language
    synonym = args.synonym
    if args.translation:
        if args.translation not in TRANSLATION:
            print('Not support in {} translation. Supported languages are:\n{}'.format(args.translation, ''.join(
                ['- ' + lang + '\n' for lang in SUPPORT_LANG])))
            logger.info('Not support in {} translation.'.format(args.translation))
            exit()
        trans = args.translation
    return_dict = OrderedDict()
    loop = asyncio.get_event_loop()
    tasks = []
    logger.info('start to work...')
    for w in args.word:
        wl = w.lower()
        return_dict[wl] = None  # guarantee the orders
        tasks.append(look_up(wl, trans, synonym, return_dict))
    loop.run_until_complete(asyncio.wait(tasks))

    # threading.Thread()
    # return_dict = OrderedDict()
    # for w in args.word:
    #     t = threading.Thread(target=look_up, name=w, args=(w, args.translation, args.dictionary, return_dict,))
    #     t.start()
    #     t.join()

    # using multiprocessing is almost the same time consume under around 7 words test, about 16 second.
    # also, the manager.dict() is a disorder dict not as good as the OrderedDict()
    # import multiprocessing
    # manager = multiprocessing.Manager()
    # return_dict = manager.dict()
    # for w in args.word:
    #     p = multiprocessing.Process(target=look_up, name=w, args=(w, args.translation, args.dictionary, return_dict,))
    #     p.start()
    #     p.join()

    for word, res in return_dict.items():
        if len(return_dict) > 1:
            print('------{}------'.format(word))
        print(res)


if __name__ == '__main__':
    main()
