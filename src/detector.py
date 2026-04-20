import cv2
import numpy as np

from config import (
    MIN_CARD_AREA,
    POLY_EPSILON_RATIO,
    SUIT_CONFIDENCE_THRESHOLD,
    RANK_CONFIDENCE_THRESHOLD,
    USE_CANNY,
)
from src.image_utils import order_points, preprocess_symbol_roi
from src.roi_extractor import (
    extract_corner_from_card,
    extract_rank_region,
    extract_suit_region,
)
from src.template_matcher import match_symbol


class CardDetector:
    def __init__(self, rank_templates, suit_templates):
        self.rank_templates = rank_templates
        self.suit_templates = suit_templates

    def find_largest_card_contour(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 60, 180)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        best = None
        best_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < MIN_CARD_AREA:
                continue

            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, POLY_EPSILON_RATIO * peri, True)

            if len(approx) == 4 and area > best_area:
                best = cnt
                best_area = area

        return best

    def warp_card(self, image, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, POLY_EPSILON_RATIO * peri, True)

        if len(approx) != 4:
            return None

        pts = approx.reshape(4, 2)
        rect = order_points(pts)

        width_a = np.linalg.norm(rect[2] - rect[3])
        width_b = np.linalg.norm(rect[1] - rect[0])
        max_width = int(max(width_a, width_b))

        height_a = np.linalg.norm(rect[1] - rect[2])
        height_b = np.linalg.norm(rect[0] - rect[3])
        max_height = int(max(height_a, height_b))

        if max_width < 50 or max_height < 80:
            return None

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype="float32")

        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))

        return warped

    def detect_rank_and_suit(self, warped_card):
        corner = extract_corner_from_card(warped_card)
        if corner is None:
            return None

        rank_roi = extract_rank_region(corner)
        suit_roi = extract_suit_region(corner)

        rank_name = "unknown"
        rank_score = 0.0
        suit_name = "unknown"
        suit_score = 0.0

        processed_rank = None
        processed_suit = None
        best_rank_template = None
        best_suit_template = None

        if rank_roi is not None:
            processed_rank = preprocess_symbol_roi(rank_roi, use_canny=USE_CANNY)
            r_name, r_score, _ = match_symbol(processed_rank, self.rank_templates)

            if r_score >= RANK_CONFIDENCE_THRESHOLD:
                rank_name = r_name
            rank_score = r_score

            if r_name in self.rank_templates:
                best_rank_template = self.rank_templates[r_name]

        if suit_roi is not None:
            processed_suit = preprocess_symbol_roi(suit_roi, use_canny=USE_CANNY)
            s_name, s_score, _ = match_symbol(processed_suit, self.suit_templates)

            if s_score >= SUIT_CONFIDENCE_THRESHOLD:
                suit_name = s_name
            suit_score = s_score

            if s_name in self.suit_templates:
                best_suit_template = self.suit_templates[s_name]

        return {
            "corner": corner,
            "rank_roi": rank_roi,
            "suit_roi": suit_roi,
            "processed_rank": processed_rank,
            "processed_suit": processed_suit,
            "rank_name": rank_name,
            "rank_score": rank_score,
            "suit_name": suit_name,
            "suit_score": suit_score,
            "best_rank_template": best_rank_template,
            "best_suit_template": best_suit_template,
        }

    def process_frame(self, frame):
        display = frame.copy()
        debug_text = "No card detected"

        contour = self.find_largest_card_contour(frame)
        if contour is None:
            return display, debug_text

        cv2.drawContours(display, [contour], -1, (0, 255, 0), 3)

        warped = self.warp_card(frame, contour)
        if warped is None:
            return display, "Card contour found but warp failed"

        result = self.detect_rank_and_suit(warped)
        if result is None:
            return display, "Could not extract card corner"

        rank_name = result["rank_name"]
        rank_score = result["rank_score"]
        suit_name = result["suit_name"]
        suit_score = result["suit_score"]

        if rank_name == "unknown" and suit_name == "unknown":
            label_text = "unknown card"
        elif rank_name == "unknown":
            label_text = f"? of {suit_name}"
        elif suit_name == "unknown":
            label_text = f"{rank_name} of ?"
        else:
            label_text = f"{rank_name} of {suit_name}"

        debug_text = f"{label_text} | Rank:{rank_score:.3f} Suit:{suit_score:.3f}"

        return display, debug_text, result, label_text
