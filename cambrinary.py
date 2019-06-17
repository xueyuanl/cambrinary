import argparse
import urllib2

from bs4 import BeautifulSoup


def load(word):
    url = 'https://dictionary.cambridge.org/dictionary/english/' + word
    response = urllib2.urlopen(url)
    html = response.read()
    return html


def parse_pronunciation(dictionary):
    """
    retrive the pronunciation for the word
    :param html: parsed_html by BeautifulSoup
    :return: string
    """
    res = ''
    header = dictionary.find('div', attrs={'class': 'pos-header'})
    uk = header.find('span', attrs={'class': 'uk'})
    us = header.find('span', attrs={'class': 'us'})
    if uk:
        uk_ipa = uk.find('span', attrs={'class': 'ipa'})
        res += 'UK ' + '/' + uk_ipa.get_text() + '/ '
    us_ipa = us.find('span', attrs={'class': 'ipa'})
    return res + 'US ' + '/' + us_ipa.get_text() + '/\n'


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
        return pos.get_text() + ' [' + sub_word.get_text() + ']\n'


def get_dictionary(args):
    """
    chose which specific dictionary would be used:
    cambridge_advanced_learners_dictionary_and_thesaurus = 'cald4'
    cambridge_academic_content_dictionary = 'cacd'
    :param args:
    :return:
    """
    raw_html = load(args.word)
    parsed_html = BeautifulSoup(raw_html, features='html.parser')
    dictionary = parsed_html.body.find('div', attrs={'class': 'dictionary', 'data-id': args.dictionary})
    if not dictionary:
        print 'No result for ' + args.word
        exit()
    return dictionary


def get_def_block(sense_block):
    res = ''
    block_title = get_sense_block_title(sense_block)
    if block_title:
        res += block_title
    sense_body = sense_block.find('div', attrs={'class': 'sense-body'})
    def_block_list = sense_body.findAll('div', attrs={'class': 'def-block pad-indent'})
    for d in def_block_list:
        definition = d.find('b', attrs={'class': 'def'})
        examps = d.findAll('div', attrs={'class': 'examp emphasized'})
        res += '* ' + definition.get_text() + '\n'
        res += ''.join(['  - ' + e.get_text().strip() + '\n' for e in examps])
    return res


def get_args():
    parser = argparse.ArgumentParser(description='A linux terminal dictionary based on cambridge online dictionary')
    parser.add_argument('-w', '--word', required=True, action='store', help='the word you want to look up')
    parser.add_argument('-d', '--dictionary', action='store', default='cald4',
                        help="to specific a dictiontry, defult(cambridge_advanced_learners_dictionary_and_thesaurus = 'cald4')")
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
    print res


if __name__ == '__main__':
    main()
