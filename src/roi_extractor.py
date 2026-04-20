from src.image_utils import rotate_if_landscape


def extract_corner_from_card(card_img):
    card_img = rotate_if_landscape(card_img)
    h, w = card_img.shape[:2]

    corner = card_img[0:int(h * 0.30), 0:int(w * 0.20)]

    if corner.size == 0:
        return None

    return corner


def extract_rank_region(corner):
    ch, cw = corner.shape[:2]

    y1 = int(ch * 0.02)
    y2 = int(ch * 0.42)

    x1 = int(cw * 0.02)
    x2 = int(cw * 0.65)

    rank_roi = corner[y1:y2, x1:x2]

    if rank_roi.size == 0:
        return None

    return rank_roi


def extract_suit_region(corner):
    ch, cw = corner.shape[:2]

    y1 = int(ch * 0.34)
    y2 = int(ch * 0.80)

    x1 = int(cw * 0.04)
    x2 = int(cw * 0.58)

    suit_roi = corner[y1:y2, x1:x2]

    if suit_roi.size == 0:
        return None

    return suit_roi