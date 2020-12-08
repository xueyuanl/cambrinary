import os
from enum import Enum
from .Conf import conf


class NoteParams(Enum):
    VOID_VALUE = 'used_but_no_value'
    NO_USE = 'not_use'

class NoteBook(object):
    file_name = 'cambrinary_notebook.yaml'

    @classmethod
    def get_notebook_path(cls):
        if conf.notebook_path == '~' or not conf.notebook_path:
            home = os.path.expanduser('~')
            return os.path.join(home, NoteBook.file_name)
        return conf.notebook_path
