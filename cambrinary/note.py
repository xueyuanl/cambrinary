import os
from enum import Enum

import yaml

from .Conf import conf
from .log import logger


class NoteParams(Enum):
    VOID_VALUE = 'used_but_no_value'
    NO_USE = 'not_use'


class NoteBook(object):
    file_name = 'cambrinary_notebook.yaml'

    @classmethod
    def _get_default_notebook_path(cls):
        if conf.notebook_path == '~' or not conf.notebook_path:
            home = os.path.expanduser('~')
            return os.path.join(home, NoteBook.file_name)
        return conf.notebook_path

    @classmethod
    def save(cls, obj, path):
        with open(path, 'a') as fh:  # append to the file
            yaml.dump(obj, fh, default_flow_style=False, encoding='utf-8', allow_unicode=True)

    @classmethod
    def get_path(cls, flag):
        notebook_path = None
        if flag != NoteParams.NO_USE.name:  # use the flag
            if flag == NoteParams.VOID_VALUE.name:  # not set value
                notebook_path = NoteBook._get_default_notebook_path()
                logger.info('default notebook path is {}'.format(notebook_path))
            else:  # set custom notebook path
                notebook_path = flag
                logger.info('get notebook path from input {}'.format(notebook_path))
            if not os.path.isfile(notebook_path):
                if os.path.isdir(notebook_path):
                    print('need Specify a file not a dir.')
                    exit()
                else:
                    print('The file {} does not exist.'.format(notebook_path))
                    print('Create it: {} for the first time.'.format(notebook_path))
                    os.mknod(notebook_path)
        return notebook_path
