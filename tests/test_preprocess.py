from NFD_Convertor import preprocess_name

def test_preprocess_name():
    assert preprocess_name('File Name.txt') == 'file_name.txt'
