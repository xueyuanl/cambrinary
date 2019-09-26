from .Conf import *


class Pron(object):
    def __init__(self):
        self.region = None
        self.lab = None
        self.ipa = None

    def to_str(self):
        pass


class Pronunciation(object):
    def __init__(self):
        self.pos = None
        self.gcs = None
        self.prons = None

    def to_str(self):
        res = ''
        if self.pos:
            res += '{} '.format(self.pos)
        if self.gcs:
            res += '[{}] '.format(self.gcs)
        if self.prons:
            res += self.prons
        return res if res == '' else res + '\n'


class PadIndent(object):
    def __init__(self, definition=None, trans=None, examps=None, synonym=None):
        self.definition = definition
        self.trans = trans
        self.examps = examps
        self.synonym = synonym

    def to_str(self):
        res = ''
        if self.definition:
            res += colors.definition('* ' + self.definition) + '\n'
        if self.trans:
            res += colors.trans_def('  {}\n'.format(self.trans))
        if self.examps:
            res += ''.join([colors.exam_sen('  - ' + e) + '\n' for e in self.examps])
        if self.synonym:
            res += '  Synonym' + '\n'
            res += self.synonym
        return res


class SenseBlock(object):
    def __init__(self, title, pad_indents):
        self.title = title  # could be None
        self.pad_indents = pad_indents  # []

    def to_str(self):
        res = ''
        if self.title:
            res += self.title
        for p in self.pad_indents:
            res += p.to_str()
        return res


class PartSpeech(object):
    def __init__(self, h_pronunciation, sense_blocks):
        self.h_pronunciation = h_pronunciation  # header
        self.sense_blocks = sense_blocks  # body []

    def to_str(self):
        res = ''
        if self.h_pronunciation:
            res += self.h_pronunciation.to_str()
        for s in self.sense_blocks:
            res += s.to_str()
        return res


class Word(object):
    def __init__(self, part_speeches):
        self.part_speeches = part_speeches  # [] for example, help is a verb or noun, each of them is a part_speech

    def to_str(self):
        res = ''
        for p in self.part_speeches:
            res += p.to_str()
        return res
