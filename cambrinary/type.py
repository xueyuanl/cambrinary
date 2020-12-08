from .Conf import *
from .country_const import *
from .log import *


class Pron(object):
    def __init__(self):
        self.region = None
        self.lab = None
        self.ipa = None

    def to_str(self):
        if self.region:
            return '{} {} '.format(self.region, self.ipa)
        else:
            return ' {} '.format(self.ipa)

    def to_dict(self):
        return {'region': self.region, 'lab': self.lab, 'ipa': self.ipa}


class Pronunciation(object):
    def __init__(self):
        self.pos = None
        self.gcs = None
        self.prons = []

    def parse_pos(self):
        pass

    def parse_gcs(self):
        pass

    def parse_prons(self):
        pass

    def parse_all(self, part_speech):
        if Word.trans == GB or Word.trans == CN:
            header = part_speech.find('div', attrs={'class': 'pos-header'})

            pos = header.findAll('span', attrs={'class': 'pos'})
            gcs = header.find('span', attrs={'class': 'gcs'})
            if pos:
                self.pos = '{}'.format(', '.join([p.get_text() for p in pos]))
            if gcs:
                self.gcs = gcs.get_text().strip()
            prons = header.findAll('span', recursive=False)
            for p in prons:
                pron = Pron()
                region = p.find('span', attrs={'class': 'region'})
                # lab = p.find('span', attrs={'class': 'lab'})
                ipa = p.find('span', attrs={'class': 'ipa'})
                if region and ipa:
                    pron.region = region.get_text().upper()
                    pron.ipa = '/{}/'.format(ipa.get_text())
                    self.prons.append(pron)
        elif Word.trans == DE or Word.trans == FR:
            di_info = part_speech.find('span', attrs={'class': 'di-info'})
            if di_info:  # like look-up has no pronunciation
                pos = di_info.find('span', attrs={'class': 'pos'})
                ipa = di_info.find('span', attrs={'class': 'ipa'})
                if pos:
                    self.pos = pos.get_text()
                if ipa:
                    pron = Pron()
                    pron.ipa = '/{}/'.format(ipa.get_text())
                    self.prons.append(pron)
        elif Word.trans in [JP, IT, KR]:
            header = part_speech.find('div', attrs={'class': 'pos-header'})
            if not header:  # word look-up in japanese
                header = part_speech.find('span', attrs={'class': 'di-info'})
            pos = header.find('span', attrs={'class': 'pos'})
            gcs = header.find('span', attrs={'class': 'gcs'})
            pron_info_list = header.findAll('span', attrs={'class': 'pron-info'})
            if pos:
                self.pos = pos.get_text()
            if gcs:
                self.gcs = gcs.get_text().strip()
            if pron_info_list:
                for pron in pron_info_list:
                    pron = Pron()
                    region = pron.find('span', attrs={'class': 'region'})
                    ipa = pron.find('span', attrs={'class': 'ipa'})
                    if region and ipa:
                        pron.region = region.get_text().upper()
                        pron.ipa = '/{}/'.format(ipa.get_text())
                        self.prons.append(pron)
        elif Word.trans == RU:
            header = part_speech.find('span', attrs={'class': 'di-info'})
            pos = header.find('span', attrs={'class': 'pos'})
            gcs = header.find('span', attrs={'class': 'gcs'})
            pron_info_list = header.findAll('span', attrs={'class': 'pron-info'})
            if pos:
                self.pos = pos.get_text()
            if gcs:
                self.gcs = gcs.get_text().strip()
            if pron_info_list:
                for pron in pron_info_list:
                    pron = Pron()
                    region = pron.find('span', attrs={'class': 'region'})
                    ipa = pron.find('span', attrs={'class': 'ipa'})
                    if region and ipa:
                        pron.region = region.get_text().upper()
                        pron.ipa = '/{}/'.format(ipa.get_text())
                        self.prons.append(pron)
        logger.info('the pronunciation is: {}'.format(self.to_str()))

    def to_str(self):
        res = ''
        if self.pos:
            res += '{} '.format(self.pos)
        if self.gcs:
            res += '[{}] '.format(self.gcs)
        for p in self.prons:
            res += p.to_str()
        return res if res == '' else res + '\n'

    def to_dict(self):
        return {'pos': self.pos, 'gcs': self.gcs, 'prons': [i.to_dict() for i in self.prons]}


class PadIndent(object):
    def __init__(self):
        self.definition = None
        self.trans = None
        self.examples = None
        self.synonym = None

    def parse_definition(self, p):
        d = p.find('div', attrs={'class': 'def ddef_d db'})
        self.definition = d.get_text() if d else None

    def parse_trans(self, body):
        trans = body.find('span', attrs={'class': 'trans dtrans dtrans-se'}, recursive=False)
        self.trans = trans.get_text().strip() if trans else None

    def parse_examples(self, body):
        examples = body.findAll('span', attrs={'class': 'eg deg'})
        self.examples = [e.get_text().strip() for e in examples] if examples else []

    def parse_synonym(self, body):
        if Word.synonym:
            synonym = body.find('div', attrs={'class': 'xref'})  # if set 'xref synonyms', can not fetch the value
            if synonym:
                logger.info('has synonym')
                self.synonym = self._parse_xref(synonym)

    def _parse_xref(xref, indent=4):
        """
        parse things like synonym, idioms
        :param xref: synonym or idioms object
        :param indent:
        :return: parsed string
        """
        res = ''
        items = xref.findAll('span', attrs={'class': 'x-h dx-h'})
        for i in items:
            res += '{}{}\n'.format(' ' * indent, i.get_text())
        return res

    def to_str(self):
        res = ''
        if self.definition:
            res += self.definition + '\n'
        if self.trans:
            res += '  {}\n'.format(self.trans)
        if self.examples:
            res += ''.join([e + '\n' for e in self.examples])
        if self.synonym:
            res += colors.synonym('  synonyms' + '\n')
            res += self.synonym
        return res

    def to_dict(self):
        return {'definition': self.definition, 'trans': self.trans,
                'examples': [i for i in self.examples], 'synonym': self.synonym}


class SenseBlock(object):
    """
    a block has multi def-blocks which give a detail definition fo the word
    """

    def __init__(self):
        self.title = None  # could be None
        self.pad_indents = []  # []

    def parse_sense_block_title(self, block):
        """
        :param block: html element BeautifulSoup object
        :return: string
        """
        dsense_h = block.find('h3', attrs={'class': 'dsense_h'})
        if dsense_h:
            logger.info('fetch the dsense_h')
            pos = dsense_h.find('span', attrs={'class': 'pos dsense_pos'})
            guideword = dsense_h.find('span', attrs={'class': 'guideword dsense_gw'})
            sub_word = guideword.find('span')
            self.title = '{} {}'.format('[' + sub_word.get_text() + ']',
                                        pos.get_text() if pos else '')
        # case for russian, words like 'get'
        sense_head = block.find('span', attrs={'class': 'sense-head'})
        if sense_head:
            guideword = sense_head.find('strong', attrs={'class': 'gw'})
            gc = sense_head.find('span', attrs={'class': 'gc'})
            self.title = '{} {}'.format(guideword.get_text(),
                                        '[' + gc.get_text() + ']' if gc else '')
        logger.info('the  title of block is {}'.format(self.title))

    def parse_pad_indents(self, block):
        sense_body = block.find('div', attrs={'class': 'sense-body dsense_b'})
        pad_indents = sense_body.findAll('div', attrs={'class': 'def-block ddef_block'})
        logger.info('the number of pad_indent is {}'.format(len(pad_indents) if pad_indents else 0))

        for pad in pad_indents:
            def_body = pad.find('span', attrs={'class': 'def-body ddef_b'})
            if not def_body:  # german dictionary use div tag
                def_body = pad.find('div', attrs={'class': 'def-body'})

            pad_indent = PadIndent()
            pad_indent.parse_definition(pad)
            pad_indent.parse_trans(def_body)
            pad_indent.parse_examples(def_body)
            pad_indent.parse_synonym(def_body)

            self.pad_indents.append(pad_indent)

    def to_str(self):
        res = ''
        if self.title:
            res += self.title + '\n'
        for p in self.pad_indents:
            res += p.to_str()
        return res

    def to_dict(self):
        return {'title': self.title, 'pad_indents': [i.to_dict() for i in self.pad_indents]}


class PartSpeech(object):

    def __init__(self):
        self.pronunciation = Pronunciation()  # header
        self.sense_blocks = []  # body []

    def parse_pronunciation(self, part_speech):
        """
        retrieve the pronunciation from part_speech
        """
        self.pronunciation.parse_all(part_speech)

    def parse_sense_blocks(self, part_speech):
        blocks = []
        blocks_with_gw = part_speech.findAll('div', attrs={'class': 'pr dsense'})  # meaning groups with guide word
        blocks.extend(blocks_with_gw)
        blocks_no_gw = part_speech.findAll('div', attrs={'class': 'pr dsense dsense-noh'})  # no guide word
        blocks.extend(blocks_no_gw)
        # some language like german or french has no 'pr dsense' or 'pr dsense dsense-noh', so use 'sense-block' to catch
        # the block
        if not blocks:
            blocks.extend(part_speech.findAll('div', attrs={'class': 'sense-block pr dsense dsense-noh'}))
        logger.info('the number of block is {}'.format(len(blocks) if blocks else 0))
        for j, block in enumerate(blocks):
            logger.info('parse the {}th block'.format(j))
            sense_block = SenseBlock()
            sense_block.parse_sense_block_title(block)
            sense_block.parse_pad_indents(block)
            self.sense_blocks.append(sense_block)

    def to_str(self):
        res = ''
        if self.pronunciation:
            res += self.pronunciation.to_str()
        for s in self.sense_blocks:
            res += s.to_str()
        return res

    def to_dict(self):
        return {'pronunciation': self.pronunciation.to_dict(), 'sense_blocks': [i.to_dict() for i in self.sense_blocks]}


class Word(object):
    trans = None
    synonym = None

    def __init__(self):
        self.part_speeches = []  # [] for example, help is a verb or noun, each of them is a part_speech

    def parse_part_speeches(self, part_speeches):
        for i, p in enumerate(part_speeches):
            logger.info('parse the {}th part_speech'.format(i))
            part_speech = PartSpeech()
            part_speech.parse_pronunciation(p)
            part_speech.parse_sense_blocks(p)
            self.part_speeches.append(part_speech)

    def to_str(self):
        res = ''
        for p in self.part_speeches:
            res += p.to_str()
        return res

    def to_dict(self):
        return {'part_speeches': [i.to_dict() for i in self.part_speeches]}
