#!/usr/bin/env python3
import argparse
import asyncio
from argparse import RawTextHelpFormatter

import aiohttp
from bs4 import BeautifulSoup

from .country_const import *
from .log import *
from .type import *

translation = {GB: 'english',
               CN: 'english-chinese-traditional',
               DE: 'english-german',
               JP: 'english-japanese',
               FR: 'english-french',
               RU: 'english-russian',
               IT: 'english-italian'}


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
    async with aiohttp.request('GET', url) as resp:
        html = await resp.text()
        return html
    # from urllib import request
    # response = request.urlopen(url)
    # html = response.read()
    # return html


def parse_xref(xref, indent=4):
    """
    parse things like synonym, idioms
    :param xref: synonym or idioms object
    :param indent:
    :return: parsed string
    """
    res = ''
    items = xref.findAll('div', attrs={'class': 'item'})
    for i in items:
        res += '{}{}\n'.format('' * indent, i.get_text())
    return res


def parse_pronunciation(part_speech, trans):
    """
    retrive the pronunciation from part_speech
    :param part_speech:
    :param trans:
    :return:
    """
    pronunciation = Pronunciation()
    if trans == GB or trans == CN:
        header = part_speech.find('div', attrs={'class': 'pos-header'})

        pos = header.findAll('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        if pos:
            pronunciation.pos = '{}'.format(', '.join([p.get_text() for p in pos]))
        if gcs:
            pronunciation.gcs = gcs.get_text().strip()
        prons = header.findAll('span', recursive=False)
        res = ''
        for p in prons:
            region = p.find('span', attrs={'class': 'region'})
            # lab = p.find('span', attrs={'class': 'lab'})
            ipa = p.find('span', attrs={'class': 'ipa'})
            if region and ipa:
                res += '{} {} '.format(
                    colors.pron_region(region.get_text().upper()),  # lab.get_text().upper() + ' ' if lab else '',
                    colors.pronunciation('/{}/'.format(ipa.get_text())))
        pronunciation.prons = res
    if trans == DE or trans == FR:
        di_info = part_speech.find('span', attrs={'class': 'di-info'})
        if di_info:  # like look-up has no pronunciation
            pos = di_info.find('span', attrs={'class': 'pos'})
            ipa = di_info.find('span', attrs={'class': 'ipa'})
            if pos:
                pronunciation.pos = pos.get_text()
            if ipa:
                pronunciation.prons = colors.pronunciation(' /{}/ '.format(ipa.get_text()))
    if trans == JP or trans == IT:
        header = part_speech.find('div', attrs={'class': 'pos-header'})
        if not header:  # word look-up in japanese
            header = part_speech.find('span', attrs={'class': 'di-info'})
        pos = header.find('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        pron_info_list = header.findAll('span', attrs={'class': 'pron-info'})
        if pos:
            pronunciation.pos = pos.get_text()
        if gcs:
            pronunciation.gcs = gcs.get_text().strip()
        if pron_info_list:
            res = ''
            for pron in pron_info_list:
                region = pron.find('span', attrs={'class': 'region'})
                ipa = pron.find('span', attrs={'class': 'ipa'})
                if region and ipa:
                    res += '{} {} '.format(colors.pron_region(region.get_text().upper()),
                                           colors.pronunciation('/{}/'.format(ipa.get_text())))
            pronunciation.prons = res
    if trans == RU:
        header = part_speech.find('span', attrs={'class': 'di-info'})
        pos = header.find('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        pron_info_list = header.findAll('span', attrs={'class': 'pron-info'})
        if pos:
            pronunciation.pos = pos.get_text()
        if gcs:
            pronunciation.gcs = gcs.get_text().strip()
        if pron_info_list:
            res = ''
            for pron in pron_info_list:
                region = pron.find('span', attrs={'class': 'region'})
                ipa = pron.find('span', attrs={'class': 'ipa'})
                if region and ipa:
                    res += '{} {} '.format(colors.pron_region(region.get_text().upper()),
                                           colors.pronunciation('/{}/'.format(ipa.get_text())))
            pronunciation.prons = res
    logger.info('the pronunciation is: '.format(pronunciation.to_str()))
    return pronunciation


def get_sense_block_title(block):
    """
    :param block: html element BeautifulSoup object
    :return: string
    """
    res = None
    dsense_h = block.find('h3', attrs={'class': 'dsense_h'})
    if dsense_h:
        logger.info('fetch the dsense_h')
        pos = dsense_h.find('span', attrs={'class': 'pos dsense_pos'})
        guideword = dsense_h.find('span', attrs={'class': 'guideword dsense_gw'})
        sub_word = guideword.find('span')
        res = '{} {}\n'.format(colors.guidword('[' + sub_word.get_text() + ']'), pos.get_text() if pos else '')
    # case for russian, words like 'get'
    sense_head = block.find('span', attrs={'class': 'sense-head'})
    if sense_head:
        guideword = sense_head.find('strong', attrs={'class': 'gw'})
        gc = sense_head.find('span', attrs={'class': 'gc'})
        res = '{} {}\n'.format(colors.guidword(guideword.get_text()), '[' + gc.get_text() + ']' if gc else '')
    logger.info('the  title of block is {}'.format(res))
    return res


def get_dictionary(html):
    """
    retrive dictionary body.
    :param html:
    :return:
    """
    PR_DICTIONARY = 'pr dictionary'
    ENTRY_BODY = 'entry-body'
    parsed_html = BeautifulSoup(html, features='html.parser')
    # this area contains all the dictionaries
    res_dict = None
    dictionaries = parsed_html.body.findAll('div', attrs={'class': PR_DICTIONARY})
    if dictionaries:  # get at least one dictionary

        res_dict = dictionaries[0]
        logger.info('get a dictionary by {}'.format(PR_DICTIONARY))
    else:  # no dictionary, just entry-body
        res_dict = parsed_html.body.find('div', attrs={'class': ENTRY_BODY})
        logger.info('get a dictionary by {}'.format(ENTRY_BODY))
    return res_dict


def parse_pad_indents(block, args):
    res = []
    sense_body = block.find('div', attrs={'class': 'sense-body dsense_b'})
    pad_indents = sense_body.findAll('div', attrs={'class': 'def-block ddef_block'})
    logger.info('the number of pad_indent is {}'.format(len(pad_indents) if pad_indents else 0))

    def get_definition(p):
        d = p.find('div', attrs={'class': 'def ddef_d'})
        return d.get_text() if d else None

    def get_trans(body):
        trans = body.find('span', attrs={'class': 'trans dtrans dtrans-se'}, recursive=False)
        return trans.get_text().strip() if trans else None

    def get_examps(body):
        examps = body.findAll('span', attrs={'class': 'eg deg'})
        return [e.get_text().strip() for e in examps] if examps else None

    def get_synonym(body, arg):
        if arg.synonym:
            synonym = body.find('div', attrs={'class': 'xref synonym'})
            if synonym:
                pad_indent.synonym = parse_xref(synonym)

    for pad in pad_indents:
        def_body = pad.find('span', attrs={'class': 'def-body ddef_b'})
        if not def_body:  # german dictionary use div tag
            def_body = pad.find('div', attrs={'class': 'def-body'})

        pad_indent = PadIndent(
            definition=get_definition(pad),
            trans=(get_trans(def_body) if def_body else None),
            examps=(get_examps(def_body) if def_body else None),
            synonym=(get_synonym(def_body, args)) if def_body else None
        )
        res.append(pad_indent)

    return res


def parse_block(block):
    """
    a block has multi def-blocks which give a detail definition fo the word
    :param block:
    :return:
    """
    args = get_args()

    sense_b = SenseBlock(
        title=get_sense_block_title(block),
        pad_indents=parse_pad_indents(block, args)
    )
    return sense_b


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
    if trans == DE:
        return dict.findAll('div', attrs={'class': 'd pr di english-german kdic'})
    if trans == JP:
        return dict.findAll('div', attrs={'class': 'pr entry-body__el'})
    if trans == FR:
        return dict.findAll('div', attrs={'class': 'd pr di english-french kdic'})
    if trans == RU or IT:
        return dict.findAll('div', attrs={'class': 'entry-body__el'}) or \
               dict.findAll('div', attrs={
                   'class': 'di $dict entry-body__el entry-body__el--smalltop clrd js-share-holder'})  # for look-up case


def parse_sense_blocks(part_speech):
    sense_blocks = []
    blocks = []
    blocks_with_gw = part_speech.findAll('div', attrs={'class': 'pr dsense'})  # meaning groups with guide word
    blocks.extend(blocks_with_gw)
    blocks_no_gw = part_speech.findAll('div', attrs={'class': 'pr dsense dsense-noh'})  # no guide word
    blocks.extend(blocks_no_gw)
    # some language like german or french has no 'pr dsense' or 'pr dsense dsense-noh', so use 'sense-block' to catch
    # the block
    if not blocks:
        blocks.extend(part_speech.findAll('div', attrs={'class': 'sense-block pr dsense dsense-noh'}))
    logger.info('the number of block is {}'.format(len(blocks) if blocks else 0))
    for j, block in enumerate(blocks):
        logger.info('parse the {}th block'.format(j))
        sense_block = parse_block(block)
        sense_blocks.append(sense_block)
    return sense_blocks


def parse_part_speeches(part_speeches, trans):
    res = []
    for i, p in enumerate(part_speeches):
        logger.info('parse the {}th part_speech'.format(i))
        part_speech = PartSpeech(
            h_pronunciation=parse_pronunciation(p, trans),
            sense_blocks=parse_sense_blocks(p)
        )
        res.append(part_speech)
    return res


async def look_up(word, trans, results):
    logger.info('begin to retrive word: [{}] in {}'.format(word, trans))
    html = await load(word, translation[trans])
    dictionary = get_dictionary(html)
    if not dictionary:
        results[word] = 'No result for {}'.format(word)
        logger.info('No result for {}'.format(word))
        return

    part_speeches = get_part_speeches(dictionary, trans)
    logger.info('the number of part_speeh is {}'.format(len(part_speeches) if part_speeches else 0))
    word_obj = Word(
        part_speeches=parse_part_speeches(part_speeches, trans)
    )
    results[word] = word_obj.to_str()


def main():
    args = get_args()
    trans = conf.default_trans_language
    if args.translation:
        if args.translation not in translation:
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
        return_dict[w] = None  # guarantee the orders
        tasks.append(look_up(w, trans, return_dict))
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
    # now = time.time()
    main()
    # end = time.time()
    # print('using time ' + str(end - now))
