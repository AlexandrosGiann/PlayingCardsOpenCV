class BlackjackHand:
    def __init__(self):
        self.cards = []

    def add_card(self, rank):
        if rank and rank != "unknown":
            self.cards.append(rank)

    def reset(self):
        self.cards.clear()

    def value(self):
        total = 0
        aces = 0

        for rank in self.cards:
            if rank in ["J", "Q", "K"]:
                total += 10
            elif rank == "A":
                total += 11
                aces += 1
            else:
                total += int(rank)

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_blackjack(self):
        return len(self.cards) == 2 and self.value() == 21

    def is_bust(self):
        return self.value() > 21

    def display(self):
        return " + ".join(self.cards) if self.cards else "-"


class BlackjackGame:
    def __init__(self):
        self.player = BlackjackHand()
        self.dealer = BlackjackHand()

    def reset(self):
        self.player.reset()
        self.dealer.reset()

    def add_player_card(self, rank):
        self.player.add_card(rank)

    def add_dealer_card(self, rank):
        self.dealer.add_card(rank)

    def result(self):
        pv = self.player.value()
        dv = self.dealer.value()

        if not self.player.cards:
            return "Scan player cards."

        if self.player.is_blackjack():
            return "PLAYER WINS - Blackjack!"

        if self.player.is_bust():
            return "DEALER WINS - Player bust."

        if not self.dealer.cards:
            return "Scan dealer cards."

        if self.dealer.is_blackjack():
            return "DEALER WINS - Blackjack!"

        if self.dealer.is_bust():
            return "PLAYER WINS - Dealer bust."

        if dv < 17:
            return "Dealer should HIT."

        if pv > dv:
            return "PLAYER WINS."

        if dv > pv:
            return "DEALER WINS."

        return "PUSH - Tie."

    def suggestion(self):
        value = self.player.value()

        if value == 0:
            return ""

        if value <= 11:
            return "Suggestion: HIT"

        if value >= 17:
            return "Suggestion: STAND"

        return "Suggestion: depends on dealer card"