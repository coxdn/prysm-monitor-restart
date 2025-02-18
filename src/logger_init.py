import sys
import re
from datetime import date

from loguru import logger

import sys
import os

# Имя основного файла скрипта
main_script_path = sys.argv[0]

# Извлекаем только имя файла
main_script_name = os.path.basename(main_script_path)


def logging_setup():

    format_info = "<green>{time:HH:mm:ss.SS}</green> <blue>{level}</blue> <level>{message}</level>"
    format_error = "<green>{time:HH:mm:ss.SS}</green> <blue>{level}</blue> | " \
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
    file_path = r"logs/"
    # if sys.platform == "win32":

    logger.remove()

    logger.add(file_path + f"{main_script_name}_out_{date.today().strftime('%m-%d')}.log", colorize=True,
               format=format_info)

    logger.add(sys.stdout, colorize=True,
               format=format_info, level="INFO")


def clean_brackets(raw_str):
    clean_text = re.sub(brackets_regex, '', raw_str)
    return clean_text


brackets_regex = re.compile(r'<.*?>')

logging_setup()
