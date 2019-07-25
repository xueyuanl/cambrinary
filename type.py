from Conf import *


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
    def __init__(self):
        self.definition = None
        self.trans = None
        self.examps = None
        self.synonym = None

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
        return res;


class SenseBlock(object):
    def __init__(self):
        self.title = None
        self.pad_indents = []

    def to_str(self):
        res = ''
        if self.title:
            res += self.title
        for p in self.pad_indents:
            res += p.to_str()
        return res


class PartSpeech(object):
    def __init__(self):
        self.pronunciation = None
        self.sense_blocks = []

    def to_str(self):
        res = ''
        if self.pronunciation:
            res += self.pronunciation.to_str()
        for s in self.sense_blocks:
            res += s.to_str()
        return res


class Word(object):
    def __init__(self):
        self.part_speeches = []

    def to_str(self):
        res = ''
        for p in self.part_speeches:
            res += p.to_str()
        return res
