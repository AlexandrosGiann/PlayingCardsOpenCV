class Card:
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    SUITS = ["club", "diamond", "heart", "spade"]

    def __init__(self, rank, suit):
        if rank not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}")

        if suit not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")

        self.rank = rank
        self.suit = suit

    @property
    def rank_value(self):
        return self.RANKS.index(self.rank) + 2

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def __eq__(self, other):
        return (
            isinstance(other, Card)
            and self.rank == other.rank
            and self.suit == other.suit
        )

    def __hash__(self):
        return hash((self.rank, self.suit))