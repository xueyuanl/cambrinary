#!/usr/bin/env python3
import argparse
import threading
from argparse import RawTextHelpFormatter
from collections import OrderedDict
from urllib import request

from bs4 import BeautifulSoup

from color import Color
from country_const import *

translation = {GB: 'english',
               CN: 'english-chinese-traditional',
               DE: 'english-german',
               JP: 'english-japanese',
               FR: 'english-french',
               RU: 'english-russian',
               IT: 'english-italian'}

colors = Color()


def get_args():
    parser = argparse.ArgumentParser(description='A linux online terminal dictionary based on cambridge dictionary',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-w', '--word', required=True, nargs='+', action='store', help='the word you want to look up')
    parser.add_argument('-t', '--translation', action='store', default='english',
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


def load(word, trans):
    url = 'https://dictionary.cambridge.org/dictionary/' + trans + '/' + word
    response = request.urlopen(url)
    html = response.read()
    return html


def color(s, formatting=0, foreground=36, background=49):
    """
    default formatting, cyan foreground and default background color.
    for reference: https://misc.flogisoft.com/bash/tip_colors_and_formatting
    :param s:
    :param formatting:
    :param foreground:
    :param background:
    :return: decorated string
    """
    pre = '\033['
    post = '\033[0m'
    return '{}{};{};{}m{}{}'.format(pre, formatting, foreground, background, s, post)


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
    res = ''
    if trans == GB or trans == CN:
        header = word_class.find('div', attrs={'class': 'pos-header'})

        pos = header.find('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        if pos:
            res += '{} '.format(pos.get_text())
        if gcs:
            res += '[{}] '.format(gcs.get_text().strip())
        prons = header.findAll('span', recursive=False)
        for p in prons:
            region = p.find('span', attrs={'class': 'region'})
            lab = p.find('span', attrs={'class': 'lab'})
            ipa = p.find('span', attrs={'class': 'ipa'})
            if region and ipa:
                res += '{} {}{} '.format(
                    colors.pron_region(region.get_text().upper()), lab.get_text().upper() + ' ' if lab else '',
                    colors.pronunciation('/{}/'.format(ipa.get_text())))
    if trans == DE or trans == FR:
        di_info = word_class.find('span', attrs={'class': 'di-info'})
        if di_info:  # like look-up has no pronunciation
            pos = di_info.find('span', attrs={'class': 'pos'})
            ipa = di_info.find('span', attrs={'class': 'ipa'})
            if pos:
                res += '{}'.format(pos.get_text())
            if ipa:
                res += colors.pronunciation(' /{}/ '.format(ipa.get_text()))
    if trans == JP or trans == IT:
        header = word_class.find('div', attrs={'class': 'pos-head'})
        if not header:  # word look-up in japanese
            header = word_class.find('span', attrs={'class': 'di-info'})
        pos = header.find('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        pron_info_list = header.findAll('span', attrs={'class': 'pron-info'})
        if pos:
            res += '{} '.format(pos.get_text())
        if gcs:
            res += '[{}] '.format(gcs.get_text().strip())
        if pron_info_list:
            for pron in pron_info_list:
                region = pron.find('span', attrs={'class': 'region'})
                ipa = pron.find('span', attrs={'class': 'ipa'})
                if region and ipa:
                    res += '{} {} '.format(colors.pron_region(region.get_text().upper()),
                                           colors.pronunciation('/{}/'.format(ipa.get_text())))
    if trans == RU:
        header = word_class.find('span', attrs={'class': 'di-info'})
        pos = header.find('span', attrs={'class': 'pos'})
        gcs = header.find('span', attrs={'class': 'gcs'})
        pron_info_list = header.findAll('span', attrs={'class': 'pron-info'})
        if pos:
            res += '{} '.format(pos.get_text())
        if gcs:
            res += '[{}] '.format(gcs.get_text().strip())
        if pron_info_list:
            for pron in pron_info_list:
                region = pron.find('span', attrs={'class': 'region'})
                ipa = pron.find('span', attrs={'class': 'ipa'})
                if region and ipa:
                    res += '{} {} '.format(colors.pron_region(region.get_text().upper()),
                                           colors.pronunciation('/{}/'.format(ipa.get_text())))
    return res if res == '' else res + '\n'


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


def get_dictionary(word, trans, dictionary):
    """
    retrive dictionary body.
    :param word:
    :param trans:
    :param dictionary:
    :return:
    """
    if trans not in translation:
        print('Not support in {} translation. Supported languages are:\n{}'.format(trans, ''.join(
            ['- ' + lang + '\n' for lang in SUPPORT_LANG])))
        exit()
    raw_html = load(word, translation[trans])
    parsed_html = BeautifulSoup(raw_html, features='html.parser')
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


def get_def_block(sense_block):
    args = get_args()
    res = ''
    block_title = get_sense_block_title(sense_block)
    if block_title:
        res += block_title
    sense_body = sense_block.find('div', attrs={'class': 'sense-body'})
    def_block_pad_indent_list = sense_body.findAll('div', attrs={'class': 'def-block pad-indent'})
    for d in def_block_pad_indent_list:
        definition = d.find('b', attrs={'class': 'def'})
        if definition:
            res += colors.definition('* ' + definition.get_text()) + '\n'
        def_body = d.find('span', attrs={'class': 'def-body'})
        if not def_body:
            def_body = d.find('div', attrs={'class': 'def-body'})  # german dictionary use div tag
        if def_body:
            trans = def_body.find('span', attrs={'class': 'trans'}, recursive=False)
            examps = def_body.findAll('span', attrs={'class': 'eg'})
            if trans:
                res += '  {}\n'.format(trans.get_text().strip())
            if examps:
                res += ''.join([colors.exam_sen('  - ' + e.get_text().strip()) + '\n' for e in examps])
            if args.synonym:
                synonym = def_body.find('div', attrs={'class': 'xref synonym'})
                if synonym:
                    res += color('  Synonym', foreground=36) + '\n'
                    res += parse_xref(synonym)

    return res


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


def look_up(word, trans, dictionary, results):
    dictionary = get_dictionary(word, trans, dictionary)
    if not dictionary:
        results[word] = 'No result for {}'.format(word)
        return
    word_class_list = get_word_class(dictionary, trans)
    res = ''
    for w in word_class_list:
        pronunciation = parse_pronunciation(w, trans)
        res += pronunciation
        sense_block_list = w.findAll('div', attrs={'class': 'sense-block'})  # one block for one meaning group.
        for i, block in enumerate(sense_block_list):
            res += get_def_block(block)
    results[word] = res


def main():
    args = get_args()
    threading.Thread()
    return_dict = OrderedDict()
    for w in args.word:
        t = threading.Thread(target=look_up, name=w, args=(w, args.translation, args.dictionary, return_dict,))
        t.start()
        t.join()

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
