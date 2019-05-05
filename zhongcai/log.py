# coding: utf-8
import logging
from logging.handlers import TimedRotatingFileHandler
class Logger:
    def __init__(self, logname, logger):
        """ 指定保存日志的文件路径，日志级别，以及调用文件
           将日志存入到指定的文件中
        """
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # fh = logging.FileHandler(logname)
        fh = TimedRotatingFileHandler(logname, encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def getlog(self):
        return self.logger

