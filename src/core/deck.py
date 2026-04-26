import random

from src.core.card import Card


class Deck:
    def __init__(self, include_jokers=False):
        self.include_jokers = include_jokers
        self.cards = self._create_deck()

    def _create_deck(self):
        cards = []

        for suit in Card.SUITS:
            for rank in Card.RANKS:
                cards.append(Card(rank, suit))

        if self.include_jokers:
            # Placeholder support for future joker handling
            cards.append("Joker")
            cards.append("Joker")

        return cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count=1):
        if count < 1:
            raise ValueError("Count must be at least 1")

        if count > len(self.cards):
            raise ValueError("Not enough cards in deck")

        drawn = self.cards[:count]
        self.cards = self.cards[count:]

        if count == 1:
            return drawn[0]

        return drawn

    def reset(self):
        self.cards = self._create_deck()

    def remaining(self):
        return len(self.cards)

    def __len__(self):
        return len(self.cards)