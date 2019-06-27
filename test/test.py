import json
import logging
import subprocess
import sys
import time
from collections import OrderedDict

logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

sys.path.append('..')
from country_const import *


def load(json_file):
    with open(json_file) as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def run_case(word, trans=None):
    time.sleep(1)  # avoid http request block
    trans_arg = ''
    if trans:
        trans_arg = '-t {} '.format(trans)
    cmd = 'python3 ../cambrinary.py {}-w {}'.format(trans_arg, word)
    try:
        if trans:
            logger.info("TEST word: " + word + " in " + trans)
        else:
            logger.info("TEST word: " + word + " in default")
        subprocess.check_output(cmd, shell=True)
    except Exception:
        logger.error("error occur when exec command: " + cmd)


def main():
    test_case = load('test_case.json')
    alphabet = test_case['alphabet']
    for a in alphabet:
        run_case(a)
        run_case(a, CN)
        run_case(a, DE)
    words = test_case['words']
    for w in words:
        run_case(w)
        run_case(w, CN)
        run_case(w, DE)
    phrases = test_case['phrases']
    for p in phrases:
        run_case(p)
        run_case(p, CN)
        run_case(p, DE)


if __name__ == '__main__':
    main()
