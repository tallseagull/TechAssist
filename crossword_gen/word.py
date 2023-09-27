import re
import random

class Word(object):
    def __init__(self, word=None, clue=None, random_factor=3):
        self.word = re.sub(r'\s', '', word.lower())
        self.clue = clue
        self.length = len(self.word)
        # the below are set when placed on board
        self.row = None
        self.col = None
        self.vertical = None
        self.number = None
        self.rank = len(self.word) + random_factor * random.random()

    def down_across(self):  # return down or across
        if self.vertical:
            return 'down'
        else:
            return 'across'

    def reset(self):
        # Forget the row, col, vertical, number:
        self.row = None
        self.col = None
        self.vertical = None
        self.number = None

    def copy(self):
        # Returns a new copy of self:
        copy = Word(self.word, self.clue)
        copy.row = self.row
        copy.col = self.col
        copy.vertical = self.vertical
        copy.number = self.number
        return copy

    def __repr__(self):
        return self.word

    def __len__(self):
        return len(self.word)
