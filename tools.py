import os
import numpy as np
from typing import Tuple


def judgeInputType(file_path: str):
    file_paths = file_path.split('/')
    # print(file_paths)
    file_name = file_paths[-1]
    file_extend = os.path.splitext(file_name)
    # print(file_extend)
    if file_extend[-1] in ['.gif', '.GIF', '.png', '.PNG', '.jpg', '.JPG', '.jpeg', '.jpeg']:
        # print('img')
        return 'img'
    else:
        return 'binary'


def dataReshape(data: np.ndarray, shape: Tuple):
    try:
        return data.reshape(shape)
    except:
        return None


def dataTranspose(data: np.ndarray, shape: Tuple):
    try:
        return data.transpose(shape)
    except:
        return None
