import argparse
import urllib2

from bs4 import BeautifulSoup


def load(word):
    url = 'https://dictionary.cambridge.org/dictionary/english/' + word
    response = urllib2.urlopen(url)
    html = response.read()
    return html


def parse_header(dictionary):
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


def get_dictionary(html_obj):
    """
    chose which specific dictionary would be used
    :param html_obj:
    :return:
    """
    cambridge_advanced_learners_dictionary_and_thesaurus = 'cald4'
    cambridge_academic_content_dictionary = 'cacd'
    return html_obj.body.find('div', attrs={'class': 'dictionary',
                                            'data-id': cambridge_advanced_learners_dictionary_and_thesaurus})


def get_args():
    parser = argparse.ArgumentParser(description='A linux terminal dictionary based on cambridge online dictionary')
    parser.add_argument('-w', '--word', required=True, action='store', help='the word you want to look up')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    raw_html = load(args.word)
    parsed_html = BeautifulSoup(raw_html, features='html.parser')
    res = ''

    dictionary = get_dictionary(parsed_html)
    if not dictionary:
        print 'No result for ' + args.word
        return
    # 'help' has verb and noun at the same time. So each of them for one entry_body_el
    entry_body_el_list = dictionary.findAll('div', attrs={'class': 'entry-body__el clrd js-share-holder'})
    for el in entry_body_el_list:
        pronunciation = parse_header(el)
        res += pronunciation
        sense_block_list = el.findAll('div', attrs={'class': 'sense-block'})  # one block for one meaning group.

        for i, block in enumerate(sense_block_list):
            block_title = get_sense_block_title(block)
            # check if the word has multi-sense block or just one
            if block_title:  # word like 'get' having muti sense block
                res += str(i + 1) + '. ' + block_title
                def_list = block.findAll('b', attrs={'class': 'def'})
                res += ''.join(['   - ' + d.get_text() + '\n' for d in def_list])
            if not block_title:  # word like 'apple' having just one block
                def_list = block.findAll('b', attrs={'class': 'def'})
                res += ''.join([str(index + 1) + '. ' + d.get_text() + '\n' for index, d in enumerate(def_list)])
    print res


if __name__ == '__main__':
    main()
