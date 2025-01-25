import logging
import os

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨을 INFO로 설정
    format=str('%(asctime)s:%(levelname)s:%(name)s: %(message)s'),
	datefmt = '%m-%d-%Y %I:%M:%S %p',
    handlers=[
        logging.StreamHandler(),  # 콘솔 출력
        logging.FileHandler(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs', 'bot.log')), encoding='utf-8')  # 파일 출력
    ]
)
logger = logging.getLogger(__name__)
