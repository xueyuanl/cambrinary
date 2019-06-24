#!/usr/bin/env python3
import argparse
from argparse import RawTextHelpFormatter
from urllib import request

from bs4 import BeautifulSoup

translation = {'english': 'english', 'chinese': 'english-chinese-traditional'}


def load(word, translation):
    url = 'https://dictionary.cambridge.org/dictionary/' + translation + '/' + word
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


def parse_pronunciation(dictionary):
    """
    retrive the pronunciation for the word
    :param dictionary:
    :return: string
    """
    res = ''
    header = dictionary.find('div', attrs={'class': 'pos-header'})
    pos = header.find('span', attrs={'class': 'pos'})
    gcs = header.find('span', attrs={'class': 'gcs'})
    uk = header.find('span', attrs={'class': 'uk'})
    us = header.find('span', attrs={'class': 'us'})
    if pos:
        res += '{} '.format(pos.get_text())
    if gcs:
        res += '[{}] '.format(gcs.get_text().strip())
    if uk:
        uk_ipa = uk.find('span', attrs={'class': 'ipa'})
        res += '{} /{}/ '.format(color('UK', foreground=34), uk_ipa.get_text())
    if us:
        us_ipa = us.find('span', attrs={'class': 'ipa'})
        res += '{} /{}/ '.format(color('US', foreground=34), us_ipa.get_text())
    return res + '\n'


def get_sense_block_title(sense_block):
    """

    :param sense_block: html element BeautifulSoup object
    :return: string
    """
    block = sense_block.find('h3', attrs={'class': 'txt-block txt-block--alt2'})
    if block:
        pos = block.find('span', attrs={'class': 'pos'})
        guideword = block.find('span', attrs={'class': 'guideword'})
        sub_word = guideword.find('span')
        return '[{}] {}\n'.format(sub_word.get_text(), pos.get_text())


def get_dictionary(args):
    """
    chose which specific dictionary would be used:
    cambridge_advanced_learners_dictionary_and_thesaurus = 'cald4'
    cambridge_academic_content_dictionary = 'cacd'
    :param args:
    :return:
    """
    raw_html = load(args.word, translation[args.translation])
    parsed_html = BeautifulSoup(raw_html, features='html.parser')
    dictionary = parsed_html.body.find('div', attrs={'class': 'dictionary'})
    if args.dictionary:
        dictionary = parsed_html.body.find('div', attrs={'class': 'dictionary', 'data-id': args.dictionary})
    if translation[args.translation] == 'english-chinese-traditional':  # for chinese
        # like word 'a ,b or c', it will get all entry-body instead of the first one, just use entry may slove this issue.
        dictionary = parsed_html.body.find('div', attrs={'class': 'entry-body'})
    if not dictionary:
        print('No result for ' + args.word)
        exit()
    return dictionary


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
        res += color('* ' + definition.get_text()) + '\n'
        def_body = d.find('span', attrs={'class': 'def-body'})
        if def_body:
            trans = def_body.find('span', attrs={'class': 'trans'}, recursive=False)
            examps = def_body.findAll('span', attrs={'class': 'eg'})
            if trans:
                res += '  {}\n'.format(trans.get_text())
            if examps:
                res += ''.join(['  - ' + e.get_text().strip() + '\n' for e in examps])
            if args.synonym:
                synonym = def_body.find('div', attrs={'class': 'xref synonym'})
                if synonym:
                    res += color('  Synonym', foreground=36) + '\n'
                    res += parse_xref(synonym)

    return res


def get_args():
    parser = argparse.ArgumentParser(description='A linux online terminal dictionary based on cambridge dictionary',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-w', '--word', required=True, action='store', help='the word you want to look up')
    parser.add_argument('-t', '--translation', action='store', default='english',
                        help="Prefered language to explain. Defult(english explaination)\n"
                             "'english' for english explaination.\n"
                             "'chinese' for english-chinese-traditional translation.")
    parser.add_argument('-d', '--dictionary', action='store',
                        help="To specific a dictiontry. But note that these dictionary only work for english explaination.\n"
                             "'cald4' for cambridge_advanced_learners_dictionary_and_thesaurus. \n"
                             "'cacd' for cambridge_academic_content_dictionary.")
    parser.add_argument('-s', '--synonym', action="store_true", help='show the synonym of the word if has')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    dictionary = get_dictionary(args)
    # 'help' has verb and noun at the same time. So each of them for one entry_body_el
    entry_body_el_list = dictionary.findAll('div', attrs={'class': 'entry-body__el clrd js-share-holder'})
    res = ''
    for el in entry_body_el_list:
        pronunciation = parse_pronunciation(el)
        res += pronunciation
        sense_block_list = el.findAll('div', attrs={'class': 'sense-block'})  # one block for one meaning group.
        for i, block in enumerate(sense_block_list):
            res += get_def_block(block)
    print(res)


if __name__ == '__main__':
    main()
