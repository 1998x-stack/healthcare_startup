import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_ROOT = os.path.join(ROOT_DIR, 'data')
LOGS_ROOT = os.path.join(ROOT_DIR, 'logs')

DEFAULT_NUM_PROCESSES = 8
DEFAULT_PAGE_TIME = 120

SITE_NAMES = ('hospital', 'medicine', 'qa')

SAVE_FOLDERS = {
    'hospital': os.path.join(SAVE_ROOT, 'hospital'),
    'medicine': os.path.join(SAVE_ROOT, 'medician'),
    'qa': os.path.join(SAVE_ROOT, 'ques_ans'),
}

SEED_DATA = {
    'beijing_csv': os.path.join(ROOT_DIR, 'yiyuandiqu-beijing.csv'),
    'beijing_json': os.path.join(ROOT_DIR, 'beijing_hospital.json'),
}