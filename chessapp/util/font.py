from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import QRect, QSize

s_min_font_size = 10
s_max_font_size = 100


def find_font_size(bounding_box: QSize, text: str):
    """finds the best font size for the given text and bounding box to fill the box with the given text. the minimum font size is
    s_min_font_size and the maximum font size is s_max_font_size. the font size is returned as the maximum lower bound thats fits
    the text inside the box (unless the text is too large for the box even with the minimum font size applied) then the minimum
    font size is returned.

    Args:
        bounding_box (QSize): bounding box of the text
        text (str): _description_

    Returns:
        _type_: _description_
    """
    font = QFont()
    low = s_min_font_size
    high = s_max_font_size
    # binary search for the best font size
    while high - low > 1:
        mid = (low + high) // 2
        font.setPointSize(mid)
        metrics = QFontMetrics(font)
        bounding_font_rect: QRect = metrics.boundingRect(text)
        if bounding_font_rect.width() > bounding_box.width() or bounding_font_rect.height() > bounding_box.height():
            high = mid
        else:
            low = mid
    return low
