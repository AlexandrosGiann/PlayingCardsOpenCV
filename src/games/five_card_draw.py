from src.core.deck import Deck
from src.core.poker_hand import PokerHandEvaluator


class FiveCardDrawGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = []
        self.dealer_hand = []
        self.result_data = None

    def start_new_game(self):
        self.deck.reset()
        self.deck.shuffle()

        self.player_hand = self.deck.draw(5)
        self.dealer_hand = self.deck.draw(5)

        self.result_data = self._evaluate()

    def _evaluate(self):
        player_eval = PokerHandEvaluator.evaluate(self.player_hand)
        dealer_eval = PokerHandEvaluator.evaluate(self.dealer_hand)

        comparison = PokerHandEvaluator.compare(player_eval, dealer_eval)

        if comparison == 1:
            winner = "PLAYER WINS"
        elif comparison == -1:
            winner = "DEALER WINS"
        else:
            winner = "PUSH (TIE)"

        return {
            "player_eval": player_eval,
            "dealer_eval": dealer_eval,
            "winner": winner
        }

    def format_hand(self, hand):
        return " | ".join([f"{c.rank}-{c.suit[0].upper()}" for c in hand])

    def get_result_text(self):
        if not self.result_data:
            return "Press Deal to start"

        p = self.result_data["player_eval"]
        d = self.result_data["dealer_eval"]

        return (
            f"PLAYER: {self.format_hand(self.player_hand)}\n"
            f"→ {p['name']}\n\n"
            f"DEALER: {self.format_hand(self.dealer_hand)}\n"
            f"→ {d['name']}\n\n"
            f"RESULT: {self.result_data['winner']}"
        )