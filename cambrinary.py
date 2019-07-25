#!/usr/bin/env python3
import argparse
import asyncio
from argparse import RawTextHelpFormatter

import aiohttp
from bs4 import BeautifulSoup

from country_const import *
from type import *

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
    parser.add_argument('-d', '--dictionary', action='store',
                        help="To specific a dictiontry. But note that these dictionary only work for english explaination.\n"
                             "'cald4' for cambridge_advanced_learners_dictionary_and_thesaurus. \n"
                             "'cacd' for cambridge_academic_content_dictionary.")
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


def parse_pronunciation(word_class, trans):
    """
    retrive the pronunciation for the word
    :param word_class:
    :return: string
    """
    pronunciation = Pronunciation()
    if trans == GB or trans == CN:
        header = word_class.find('div', attrs={'class': 'pos-header'})

        pos = header.find('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        if pos:
            pronunciation.pos = pos.get_text()
        if gcs:
            pronunciation.gcs = gcs.get_text().strip()
        prons = header.findAll('span', recursive=False)
        res = ''
        for p in prons:
            region = p.find('span', attrs={'class': 'region'})
            lab = p.find('span', attrs={'class': 'lab'})
            ipa = p.find('span', attrs={'class': 'ipa'})
            if region and ipa:
                res += '{} {}{} '.format(
                    colors.pron_region(region.get_text().upper()), lab.get_text().upper() + ' ' if lab else '',
                    colors.pronunciation('/{}/'.format(ipa.get_text())))
        pronunciation.prons = res
    if trans == DE or trans == FR:
        di_info = word_class.find('span', attrs={'class': 'di-info'})
        if di_info:  # like look-up has no pronunciation
            pos = di_info.find('span', attrs={'class': 'pos'})
            ipa = di_info.find('span', attrs={'class': 'ipa'})
            if pos:
                pronunciation.pos = pos.get_text()
            if ipa:
                pronunciation.prons = colors.pronunciation(' /{}/ '.format(ipa.get_text()))
    if trans == JP or trans == IT:
        header = word_class.find('div', attrs={'class': 'pos-head'})
        if not header:  # word look-up in japanese
            header = word_class.find('span', attrs={'class': 'di-info'})
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
        header = word_class.find('span', attrs={'class': 'di-info'})
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
    return pronunciation


def get_sense_block_title(sense_block):
    """
    :param sense_block: html element BeautifulSoup object
    :return: string
    """
    txt_block = sense_block.find('h3', attrs={'class': 'txt-block txt-block--alt2'})
    if txt_block:
        pos = txt_block.find('span', attrs={'class': 'pos'})
        guideword = txt_block.find('span', attrs={'class': 'guideword'})
        sub_word = guideword.find('span')
        return '{} {}\n'.format(colors.guidword('[' + sub_word.get_text() + ']'), pos.get_text() if pos else '')
    # case for russian, words like 'get'
    sense_head = sense_block.find('span', attrs={'class': 'sense-head'})
    if sense_head:
        guideword = sense_head.find('strong', attrs={'class': 'gw'})
        gc = sense_head.find('span', attrs={'class': 'gc'})
        return '{} {}\n'.format(colors.guidword(guideword.get_text()), '[' + gc.get_text() + ']' if gc else '')


def get_dictionary(html, dictionary):
    """
    retrive dictionary body.
    :param html:
    :param dictionary:
    :return:
    """
    parsed_html = BeautifulSoup(html, features='html.parser')
    # this area contains all the dictionaries
    cdo_dblclick_area = parsed_html.body.find('div', attrs={'class': 'cdo-dblclick-area'})
    if not cdo_dblclick_area:
        return
    res_dict = None
    # get a custom dictionary
    if dictionary:
        res_dict = cdo_dblclick_area.find('div', attrs={'class': 'dictionary', 'data-id': dictionary})
    if not res_dict:  # cannot retrieve a specific dict even if a given args.dictionary
        # multi-dictionary or one entry-body
        dictionaries = cdo_dblclick_area.findAll('div', attrs={'class': 'dictionary'})
        if dictionaries:  # get at least one dictionary
            res_dict = dictionaries[0]
        if not dictionaries:  # no dictionary, just entry-body
            res_dict = parsed_html.body.find('div', attrs={'class': 'entry-body'})

    return res_dict


def parse_sense_block(sense_block):
    args = get_args()
    sense_b = SenseBlock()
    sense_b.title = get_sense_block_title(sense_block)
    sense_body = sense_block.find('div', attrs={'class': 'sense-body'})
    def_block_pad_indent_list = sense_body.findAll('div', attrs={'class': 'def-block pad-indent'})
    for d in def_block_pad_indent_list:
        pad_indent = PadIndent()
        definition = d.find('b', attrs={'class': 'def'})
        if definition:
            pad_indent.definition = definition.get_text()
        def_body = d.find('span', attrs={'class': 'def-body'})
        if not def_body:
            def_body = d.find('div', attrs={'class': 'def-body'})  # german dictionary use div tag
        if def_body:
            trans = def_body.find('span', attrs={'class': 'trans'}, recursive=False)
            examps = def_body.findAll('span', attrs={'class': 'eg'})
            if trans:
                pad_indent.trans = trans.get_text().strip()
            if examps:
                pad_indent.examps = [e.get_text().strip() for e in examps]
            if args.synonym:
                synonym = def_body.find('div', attrs={'class': 'xref synonym'})
                if synonym:
                    pad_indent.synonym = parse_xref(synonym)
        sense_b.pad_indents.append(pad_indent)
    return sense_b


def get_word_class(dict, trans):
    """
    'help' has verb and noun at the same time. So each of them for one part of speech(pos)
    :param dict: dictionary
    :param trans: translation language
    :return: a list of pos
    """
    if trans == GB or trans == CN:
        return dict.findAll('div', attrs={'class': 'entry-body__el clrd js-share-holder'})
    if trans == DE:
        return dict.findAll('div', attrs={
            'class': 'di english-german kdict entry-body__el entry-body__el--smalltop clrd js-share-holder'})
    if trans == JP:
        return dict.findAll('div',
                            attrs={'class': 'di $dict entry-body__el entry-body__el--smalltop clrd js-share-holder'})
    if trans == FR:
        return dict.findAll('div',
                            attrs={
                                'class': 'di english-french kdict entry-body__el entry-body__el--smalltop clrd js-share-holder'})
    if trans == RU or IT:
        res = dict.findAll('div', attrs={'class': 'di $ entry-body__el entry-body__el--smalltop clrd js-share-holder'})
        if res:
            return res
        res = dict.findAll('div', attrs={
            'class': 'di $dict entry-body__el entry-body__el--smalltop clrd js-share-holder'})  # for look-up case
        if res:
            return res


async def look_up(word, trans, dict, results):
    html = await load(word, translation[trans])
    dictionary = get_dictionary(html, dict)
    if not dictionary:
        results[word] = 'No result for {}'.format(word)
        return
    word_class_list = get_word_class(dictionary, trans)
    word_obj = Word()
    for w in word_class_list:
        part_speech = PartSpeech()
        pronunciation = parse_pronunciation(w, trans)
        part_speech.pronunciation = pronunciation
        sense_block_list = w.findAll('div', attrs={'class': 'sense-block'})  # one block for one meaning group.
        for i, block in enumerate(sense_block_list):
            sense_block = parse_sense_block(block)
            part_speech.sense_blocks.append(sense_block)
        word_obj.part_speeches.append(part_speech)
    results[word] = word_obj.to_str()


def main():
    args = get_args()
    trans = conf.default_trans_language
    if args.translation:
        if args.translation not in translation:
            print('Not support in {} translation. Supported languages are:\n{}'.format(args.translation, ''.join(
                ['- ' + lang + '\n' for lang in SUPPORT_LANG])))
            exit()
        trans = args.translation
    return_dict = OrderedDict()
    loop = asyncio.get_event_loop()
    tasks = []

    for w in args.word:
        return_dict[w] = None  # guarantee the orders
        tasks.append(look_up(w, trans, args.dictionary, return_dict))
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
