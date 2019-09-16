import logging

logging.basicConfig(filename='dict.log',
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger('cambrinary')
