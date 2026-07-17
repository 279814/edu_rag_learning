import logging


def method_name():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('Example1')
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')


def method_name2():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    logger = logging.getLogger('Example2')
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

def method_name3():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='a'
    )
    logger = logging.getLogger('Example3')
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

def method_name4():
    logger = logging.getLogger('Example4')
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    console_logger = logging.StreamHandler()
    console_logger.setLevel(level=logging.INFO)

    file_logger = logging.FileHandler(filename='app.log', mode='a')
    file_logger.setLevel(level=logging.DEBUG)

    console_logger.setFormatter(formatter)
    file_logger.setFormatter(formatter)

    logger.addHandler(console_logger)
    logger.addHandler(file_logger)

    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

if __name__ == '__main__':
    # method_name()
    # method_name2()
    # method_name3()
    method_name4()
