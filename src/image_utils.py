import cv2
import numpy as np

from config import TEMPLATE_SIZE, THRESH_BINARY_VALUE


def safe_resize(img, size):
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)


def order_points(pts):
    pts = np.array(pts, dtype="float32")

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")


def rotate_if_landscape(card_img):
    h, w = card_img.shape[:2]
    if w > h:
        card_img = cv2.rotate(card_img, cv2.ROTATE_90_CLOCKWISE)
    return card_img


def preprocess_binary_from_bgr(img_bgr, use_canny=False):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    if use_canny:
        binary = cv2.Canny(gray, 50, 150)
    else:
        _, binary = cv2.threshold(
            gray,
            THRESH_BINARY_VALUE,
            255,
            cv2.THRESH_BINARY_INV
        )

    return binary


def _get_valid_contours(binary_img):
    contours, _ = cv2.findContours(
        binary_img,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return []

    img_h, img_w = binary_img.shape[:2]
    min_area = (img_h * img_w) * 0.01

    valid = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= min_area:
            valid.append(cnt)

    return valid


def isolate_main_symbol(binary_img, symbol_size=70):
    """
    Για suits ή single-character ranks.
    Κρατά μόνο το μεγαλύτερο contour.
    """
    valid_contours = _get_valid_contours(binary_img)

    if not valid_contours:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    largest = max(valid_contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    if w < 5 or h < 5:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    cropped = binary_img[y:y + h, x:x + w]

    canvas = np.zeros((TEMPLATE_SIZE[1], TEMPLATE_SIZE[0]), dtype=np.uint8)
    resized = safe_resize(cropped, (symbol_size, symbol_size))

    y_off = (TEMPLATE_SIZE[1] - resized.shape[0]) // 2
    x_off = (TEMPLATE_SIZE[0] - resized.shape[1]) // 2

    canvas[y_off:y_off + resized.shape[0], x_off:x_off + resized.shape[1]] = resized
    return canvas


def isolate_rank_symbol(binary_img, symbol_width=70, symbol_height=70):
    """
    Για ranks. Υποστηρίζει και '10' ενώνοντας όλα τα σημαντικά contours
    σε ένα κοινό bounding box.
    """
    valid_contours = _get_valid_contours(binary_img)

    if not valid_contours:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    xs, ys, xe, ye = [], [], [], []

    for cnt in valid_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= 5 and h >= 5:
            xs.append(x)
            ys.append(y)
            xe.append(x + w)
            ye.append(y + h)

    if not xs:
        return safe_resize(binary_img, TEMPLATE_SIZE)

    x1, y1 = min(xs), min(ys)
    x2, y2 = max(xe), max(ye)

    cropped = binary_img[y1:y2, x1:x2]

    canvas = np.zeros((TEMPLATE_SIZE[1], TEMPLATE_SIZE[0]), dtype=np.uint8)
    resized = safe_resize(cropped, (symbol_width, symbol_height))

    y_off = (TEMPLATE_SIZE[1] - resized.shape[0]) // 2
    x_off = (TEMPLATE_SIZE[0] - resized.shape[1]) // 2

    canvas[y_off:y_off + resized.shape[0], x_off:x_off + resized.shape[1]] = resized
    return canvas


def preprocess_symbol_roi(roi, use_canny=False, symbol_size=70):
    binary = preprocess_binary_from_bgr(roi, use_canny=use_canny)
    isolated = isolate_main_symbol(binary, symbol_size=symbol_size)
    return isolated


def preprocess_rank_roi(roi, use_canny=False, symbol_width=75, symbol_height=70):
    binary = preprocess_binary_from_bgr(roi, use_canny=use_canny)
    isolated = isolate_rank_symbol(
        binary,
        symbol_width=symbol_width,
        symbol_height=symbol_height
    )
    return isolated


def stack_debug_panel(rank_img, rank_template, suit_img, suit_template):
    def ensure(img):
        if img is None:
            return np.zeros((120, 120), dtype=np.uint8)
        return safe_resize(img, (120, 120))

    rank_img = ensure(rank_img)
    rank_template = ensure(rank_template)
    suit_img = ensure(suit_img)
    suit_template = ensure(suit_template)

    top_left = cv2.cvtColor(rank_img, cv2.COLOR_GRAY2BGR)
    top_right = cv2.cvtColor(rank_template, cv2.COLOR_GRAY2BGR)
    bottom_left = cv2.cvtColor(suit_img, cv2.COLOR_GRAY2BGR)
    bottom_right = cv2.cvtColor(suit_template, cv2.COLOR_GRAY2BGR)

    top = np.hstack([top_left, top_right])
    bottom = np.hstack([bottom_left, bottom_right])
    panel = np.vstack([top, bottom])

    return panel