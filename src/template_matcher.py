import os
import cv2
import numpy as np

from config import TEMPLATE_SIZE
from src.image_utils import (
    preprocess_binary_from_bgr,
    isolate_main_symbol,
    preprocess_rank_roi,
    safe_resize,
)


def preprocess_template(path, use_canny=False, template_type="suit"):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Template not found: {path}")

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    if template_type == "rank":
        return preprocess_rank_roi(
            img,
            use_canny=use_canny,
            symbol_width=75,
            symbol_height=70
        )

    binary = preprocess_binary_from_bgr(img, use_canny=use_canny)
    isolated = isolate_main_symbol(binary, symbol_size=70)
    return isolated


def load_templates(folder, use_canny=False, template_type="suit"):
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Template folder not found: {folder}")

    templates = {}

    for file_name in sorted(os.listdir(folder)):
        if not file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue

        name = os.path.splitext(file_name)[0]
        path = os.path.join(folder, file_name)
        templates[name] = preprocess_template(
            path,
            use_canny=use_canny,
            template_type=template_type
        )

    if not templates:
        raise ValueError(f"No templates loaded from: {folder}")

    return templates


def match_symbol(processed_roi, templates):
    best_name = None
    best_score = -1.0
    all_scores = {}

    roi = safe_resize(processed_roi, TEMPLATE_SIZE)

    for name, tmpl in templates.items():
        tmpl = safe_resize(tmpl, TEMPLATE_SIZE)

        diff = cv2.absdiff(roi, tmpl)
        diff_score = np.sum(diff) / 255.0

        max_pixels = TEMPLATE_SIZE[0] * TEMPLATE_SIZE[1]
        similarity = 1.0 - (diff_score / max_pixels)

        all_scores[name] = similarity

        if similarity > best_score:
            best_score = similarity
            best_name = name

    return best_name, best_score, all_scores