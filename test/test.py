# run this test script in cambrinary dir.
import argparse
import json
import logging
import subprocess
import sys
import time
from argparse import RawTextHelpFormatter
from collections import OrderedDict

logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

sys.path.append('.')  # for python3 test/test.py
from cambrinary.country_const import *


def get_args():
    parser = argparse.ArgumentParser(description='test for cambrinary', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-t', '--translation', action='store',
                        help="Prefered language to test. eg: python3 test/test.py -t")
    args = parser.parse_args()
    return args


def load(json_file):
    with open(json_file) as f:
        return json.load(f, object_pairs_hook=OrderedDict)


test_case = load('test/test_case.json')


def run_case(word, trans=None):
    time.sleep(2)  # avoid http request block
    trans_arg = ''
    if trans:
        trans_arg = '-t {} '.format(trans)
    cmd = 'cambrinary {}-w {}'.format(trans_arg, word)
    try:
        if trans:
            logger.info("TEST word " + word + " in " + trans)
        else:
            logger.info("TEST word " + word + " in default")
        subprocess.check_output(cmd, shell=True)
    except Exception:
        logger.error("error occur when exec command: " + cmd)


def run_test(lang):
    logger.info('Comming to test language: ' + lang)
    alphabet = test_case['alphabet']
    for a in alphabet:
        run_case(a, lang)
    words = test_case['words']
    for w in words:
        run_case(w, lang)
    phrases = test_case['phrases']
    for p in phrases:
        run_case(p, lang)


def main():
    args = get_args()
    if args.translation:
        if args.translation not in SUPPORT_LANG:
            logger.info('Not support this language yet.')
        run_test(args.translation)
        return
    for lang in SUPPORT_LANG:
        run_test(lang)


if __name__ == '__main__':
    main()
