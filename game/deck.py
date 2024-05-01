import random

from game.card import Card

suits = [':heart_suit:', ':diamond_suit:', ':club_suit:', ':spade_suit:']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Deck:
    def __init__(self):
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()