import json
import os
from collections import OrderedDict
from pathlib import Path

from .color_const import *


def load(json_file):
    with open(json_file) as f:
        return json.load(f, object_pairs_hook=OrderedDict)


class ColorScheme(object):
    def __init__(self, pron_region, definition, exam_sen, trans_def, pronunciation, guidword):
        self.pron_region = pron_region
        self.definition = definition
        self.exam_sen = exam_sen
        self.trans_def = trans_def
        self.pronunciation = pronunciation
        self.guidword = guidword

    def to_dic(self):
        json_dic = OrderedDict()
        json_dic['pron_region'] = self.pron_region
        json_dic['definition'] = self.definition
        json_dic['exam_sen'] = self.exam_sen
        json_dic['trans_def'] = self.trans_def
        json_dic['pronunciation'] = self.pronunciation
        json_dic['guidword'] = self.guidword
        return json_dic

    @staticmethod
    def to_obj(color_scheme_dict):
        return ColorScheme(color_scheme_dict['pron_region'], color_scheme_dict['definition'],
                           color_scheme_dict['example_sentence'], color_scheme_dict['trans_definition'],
                           color_scheme_dict['pronunciation'], color_scheme_dict['guidword'])


class Conf(object):
    def __init__(self, path):
        self.conf_dict = load(path)
        self.color_scheme = ColorScheme.to_obj(self.conf_dict['color_scheme'])
        self.default_trans_language = self.conf_dict['default_trans_language']

    def to_dic(self):
        json_dic = OrderedDict()
        json_dic['color_scheme'] = self.color_scheme
        json_dic['default_trans_language'] = self.default_trans_language
        return json_dic


class Color(object):
    def __init__(self, color_scheme):
        self.color_scheme = color_scheme

    @staticmethod
    def color(s, color_scheme):
        """
        for reference: https://misc.flogisoft.com/bash/tip_colors_and_formatting
        :param s: str to color
        :param color_scheme: refer it in `color_const.py`
        :return: colored str
        """
        pre = '\033['
        post = '\033[0m'
        return '{}{};{};{}m{}{}'.format(pre, format_dic[color_scheme[0]], foreground_dic[color_scheme[1]],
                                        background_dic[color_scheme[2]], s, post)

    def pron_region(self, str):
        return self.color(str, self.color_scheme.pron_region)

    def pronunciation(self, str):
        return self.color(str, self.color_scheme.pronunciation)

    def definition(self, str):
        return self.color(str, self.color_scheme.definition)

    def trans_def(self, str):
        return self.color(str, self.color_scheme.trans_def)

    def exam_sen(self, str):
        return self.color(str, self.color_scheme.exam_sen)

    def guidword(self, str):
        return self.color(str, self.color_scheme.guidword)


try:
    cfg = Path(os.environ['XDG_CONFIG_HOME']).absolute() / 'cambrinary' / 'conf.json'
except KeyError:
    cfg = Path(os.environ['HOME']).absolute() / '.config' / 'cambrinary' / 'conf.json'
if not cfg.is_file():
    cfg = Path(__file__).absolute().parent / 'conf.json'
conf = Conf(str(cfg))
colors = Color(conf.color_scheme)
