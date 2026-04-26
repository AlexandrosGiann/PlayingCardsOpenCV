from collections import Counter

from src.core.card import Card


class PokerHandEvaluator:
    HAND_RANKS = {
        "High Card": 1,
        "One Pair": 2,
        "Two Pair": 3,
        "Three of a Kind": 4,
        "Straight": 5,
        "Flush": 6,
        "Full House": 7,
        "Four of a Kind": 8,
        "Straight Flush": 9,
        "Royal Flush": 10,
    }

    @staticmethod
    def evaluate(cards):
        """
        Evaluates exactly 5 cards.
        Returns:
        {
            "name": str,
            "rank": int,
            "values": list[int]
        }
        """
        if len(cards) != 5:
            raise ValueError("PokerHandEvaluator currently requires exactly 5 cards")

        for card in cards:
            if not isinstance(card, Card):
                raise TypeError("All items must be Card instances")

        values = sorted([card.rank_value for card in cards], reverse=True)
        suits = [card.suit for card in cards]

        value_counts = Counter(values)
        count_groups = sorted(
            value_counts.items(),
            key=lambda item: (item[1], item[0]),
            reverse=True
        )

        is_flush = len(set(suits)) == 1
        is_straight, straight_high = PokerHandEvaluator._is_straight(values)

        if is_flush and values == [14, 13, 12, 11, 10]:
            return PokerHandEvaluator._result("Royal Flush", [14])

        if is_flush and is_straight:
            return PokerHandEvaluator._result("Straight Flush", [straight_high])

        if 4 in value_counts.values():
            four_value = [v for v, c in value_counts.items() if c == 4][0]
            kicker = [v for v in values if v != four_value][0]
            return PokerHandEvaluator._result("Four of a Kind", [four_value, kicker])

        if sorted(value_counts.values()) == [2, 3]:
            three_value = [v for v, c in value_counts.items() if c == 3][0]
            pair_value = [v for v, c in value_counts.items() if c == 2][0]
            return PokerHandEvaluator._result("Full House", [three_value, pair_value])

        if is_flush:
            return PokerHandEvaluator._result("Flush", values)

        if is_straight:
            return PokerHandEvaluator._result("Straight", [straight_high])

        if 3 in value_counts.values():
            three_value = [v for v, c in value_counts.items() if c == 3][0]
            kickers = [v for v in values if v != three_value]
            return PokerHandEvaluator._result("Three of a Kind", [three_value] + kickers)

        pairs = sorted(
            [v for v, c in value_counts.items() if c == 2],
            reverse=True
        )

        if len(pairs) == 2:
            kicker = [v for v in values if v not in pairs][0]
            return PokerHandEvaluator._result("Two Pair", pairs + [kicker])

        if len(pairs) == 1:
            pair_value = pairs[0]
            kickers = [v for v in values if v != pair_value]
            return PokerHandEvaluator._result("One Pair", [pair_value] + kickers)

        return PokerHandEvaluator._result("High Card", values)

    @staticmethod
    def compare(hand_a, hand_b):
        """
        Compare two evaluation results.
        Returns:
        1  if hand_a wins
        -1 if hand_b wins
        0  if tie
        """
        if hand_a["rank"] > hand_b["rank"]:
            return 1

        if hand_a["rank"] < hand_b["rank"]:
            return -1

        for a, b in zip(hand_a["values"], hand_b["values"]):
            if a > b:
                return 1
            if a < b:
                return -1

        return 0

    @staticmethod
    def _is_straight(values):
        unique = sorted(set(values), reverse=True)

        if len(unique) != 5:
            return False, None

        # A-2-3-4-5 straight
        if unique == [14, 5, 4, 3, 2]:
            return True, 5

        for i in range(4):
            if unique[i] - unique[i + 1] != 1:
                return False, None

        return True, unique[0]

    @staticmethod
    def _result(name, values):
        return {
            "name": name,
            "rank": PokerHandEvaluator.HAND_RANKS[name],
            "values": values,
        }