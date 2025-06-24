import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from NFD_Convertor import preprocess_name

def test_preprocess_name():
    assert preprocess_name('File Name.txt') == 'file_name.txt'
