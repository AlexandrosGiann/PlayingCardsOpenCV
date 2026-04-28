from src.core.deck import Deck


class WarGame:
    def __init__(self):
        self.deck = Deck()
        self.player_pile = []
        self.dealer_pile = []
        self.table = []
        self.result = "Press Deal"

    def start_game(self):
        self.deck.reset()
        self.deck.shuffle()

        cards = self.deck.draw(52)

        self.player_pile = cards[:26]
        self.dealer_pile = cards[26:]
        self.table = []

        self.result = "Game started"

    def play_round(self):
        if not self.player_pile or not self.dealer_pile:
            self.result = "Game over"
            return

        p_card = self.player_pile.pop(0)
        d_card = self.dealer_pile.pop(0)

        self.table.extend([p_card, d_card])

        self._resolve_battle(p_card, d_card)

    def _resolve_battle(self, p_card, d_card):
        if p_card.rank_value > d_card.rank_value:
            self.player_pile.extend(self.table)
            self.table = []
            self.result = "PLAYER wins round"

        elif d_card.rank_value > p_card.rank_value:
            self.dealer_pile.extend(self.table)
            self.table = []
            self.result = "DEALER wins round"

        else:
            self.result = "WAR!"
            self._war()

    def _war(self):
        if len(self.player_pile) < 4 or len(self.dealer_pile) < 4:
            self.result = "Not enough cards for war"
            return

        for _ in range(3):
            self.table.append(self.player_pile.pop(0))
            self.table.append(self.dealer_pile.pop(0))

        p_card = self.player_pile.pop(0)
        d_card = self.dealer_pile.pop(0)

        self.table.extend([p_card, d_card])

        self._resolve_battle(p_card, d_card)

    def status(self):
        return (
            f"Player: {len(self.player_pile)} cards\n"
            f"Dealer: {len(self.dealer_pile)} cards\n"
            f"{self.result}"
        )
