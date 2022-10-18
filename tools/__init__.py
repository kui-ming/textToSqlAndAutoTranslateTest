
def is_contains_chinese(text):
    """
    判断文本中是否存在中文字符，如果存在返回真，否则返回假
    :param text: 源文本
    :return:
    """
    for c in text:
        if '\u4e00' <= c <= '\u9fa5':
            return True
    return False
