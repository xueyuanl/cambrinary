import os
from enum import Enum

import yaml

from .Conf import conf


class NoteParams(Enum):
    VOID_VALUE = 'used_but_no_value'
    NO_USE = 'not_use'


class NoteBook(object):
    file_name = 'cambrinary_notebook.yaml'

    @classmethod
    def get_default_notebook_path(cls):
        if conf.notebook_path == '~' or not conf.notebook_path:
            home = os.path.expanduser('~')
            return os.path.join(home, NoteBook.file_name)
        return conf.notebook_path

    @classmethod
    def save(cls, obj, path):
        with open(path, 'a') as fh:  # append to the file
            yaml.dump(obj, fh, default_flow_style=False, encoding='utf-8', allow_unicode=True)
