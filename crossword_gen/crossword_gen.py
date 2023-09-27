# Taken from here: https://github.com/jeremy886/crossword_helmig/blob/master/crossword_puzzle.py
import random, re, time, string
from collections import defaultdict
from copy import copy as duplicate
import pandas as pd
from crossword_gen.word import Word

class Crossword(object):
    def __init__(self, cols, rows, empty='-', maxloops=2000, available_words=None, extra_words=None, letters=None,
                 rtl=False):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.maxloops = maxloops
        self.available_words = self._gen_word_list(available_words) if available_words is not None else []
        self.extra_words = self._gen_word_list(extra_words) if extra_words is not None else []
        self.randomize_word_list()
        self.rtl = rtl  # Is this right to left? (e.g. hebrew)
        self.grid_index = None
        self.fit_score_cache = {}

        self.current_word_list = []
        self.debug = 0

        if letters is None:
            self.letters = string.ascii_lowercase
        else:
            self.letters = letters

        self.clear_grid()

    def _gen_word_list(self, words_in):
        temp_list = []
        for word in words_in:
            if isinstance(word, Word):
                temp_list.append(Word(word.word, word.clue))
            else:
                temp_list.append(Word(word[0], word[1]))
        return temp_list

    def clear_grid(self):  # initialize grid and fill with empty character
        self.grid = [[self.empty for j in range(self.cols)] for i in range(self.rows)]
        self.grid_index = defaultdict(list)
        self.fit_score_cache = {}

    def _randomize_word_list_ord(self, words_list):
        if words_list:
            # random.shuffle(words_list)  # randomize word list
            words_list.sort(key=lambda w: w.rank, reverse=True)  # sort by length

    def randomize_word_list(self):  # also resets words and sorts by length
        self._randomize_word_list_ord(self.available_words)
        self._randomize_word_list_ord(self.extra_words)

    def reset_words(self):
        """
        Reset the words in self.current_wordlist to remove any location or numbering:
        :return:
        """
        for word in self.current_word_list:
            word.reset()

    def _score_grid(self, grid):
        """
        Score the grid - convert to a dataframe, delete empty rows / cols, score ration of white to black cells:
        :param grid: A list of lists (2D list) with the grid
        :return:
        """
        new_grid = pd.DataFrame(grid)
        # Columns removal:
        cols_to_remove = []
        for col in range(new_grid.shape[1]):
            if (new_grid.iloc[:, col] == self.empty).all():
                cols_to_remove.append(col)
        if cols_to_remove:
            new_grid = new_grid.drop(columns=cols_to_remove)

        # Now the rows:
        rows_to_remove = []
        for row in range(new_grid.shape[0]):
            if (new_grid.iloc[row, :] == self.empty).all():
                rows_to_remove.append(row)
        if rows_to_remove:
            new_grid = new_grid.drop(index=rows_to_remove)

        black_cells = (new_grid==self.empty).sum().sum()
        white_cells = new_grid.shape[0] * new_grid.shape[1]
        res = 100*white_cells / black_cells
        return res

    def compute_crossword(self, time_permitted=5.00, spins=3):
        """
        Try to create crosswords, and choose the best one we have
        :param time_permitted: The time in seconds we allow this to run
        :param spins: The number of times we try to add words in each cycle
        :return:
        """
        time_permitted = float(time_permitted)

        count = 0
        best_score = -1
        copy = Crossword(self.cols, self.rows, self.empty, self.maxloops, self.available_words, self.extra_words,
                         self.letters, self.rtl)

        start_full = float(time.time())
        while (float(time.time()) - start_full) < time_permitted or count == 0:  # only run for x seconds
            self.debug += 1
            copy.current_word_list = []
            copy.clear_grid()
            copy.randomize_word_list()
            copy.reset_words()
            x = 0
            while x < spins:  # spins; 2 seems to be plenty
                for word in copy.available_words:
                    if word not in copy.current_word_list:
                        copy.fit_and_add(word)
                x += 1

            # Now try to add some extra words:
            extra_added = 0
            for word in copy.extra_words:
                if word not in copy.current_word_list:
                    if(copy.fit_and_add(word)):
                        extra_added += 1
                if extra_added > 3:
                    break

            # buffer the best crossword by comparing placed words
            if len(copy.current_word_list) >= len(self.current_word_list):
                # Score how compact the result is - ratio of white cells to black cells:
                score = self._score_grid(copy.grid)
                if score > best_score:
                    self.current_word_list = [w.copy() for w in copy.current_word_list]
                    self.grid = copy.grid
                    best_score = score
            count += 1
        print(f"Calculated {count} copies in the process")
        return

    def _index_grid_letters(self):
        """
        Builds an index from letter to all locations in the grid containing that letter. Used to speed up the calculation
        of suggested coords. Saves the index in self.grid_index
        :return: None
        """
        self.grid_index = defaultdict(list)
        for rowc, row in enumerate(self.grid):
            for colc, letter in enumerate(row):
                if letter != self.empty:
                    self.grid_index[letter].append((rowc+1, colc+1))

    def suggest_coord(self, word):
        """
        Suggest locations for a word. Looks for one letter matches to suggest with existing words on the grid
        :param word:
        :return:
        """
        if self.grid_index is None:
            self._index_grid_letters()
        coordlist = []
        for glc, given_letter in enumerate(word.word):  # cycle through letters in word
            for rowc, colc in self.grid_index[given_letter]:
                if rowc - glc > 0:  # make sure we're not suggesting a starting point off the grid
                    if ((rowc - glc) + word.length) <= self.rows:  # make sure word doesn't go off of grid
                        coordlist.append([colc, rowc - glc, 1, colc + (rowc - glc), 0])
                if colc - glc > 0:  # make sure we're not suggesting a starting point off the grid
                    if ((colc - glc) + word.length) <= self.cols:  # make sure word doesn't go off of grid
                        coordlist.append([colc - glc, rowc, 0, rowc + (colc - glc), 0])


                    # example: coordlist[0] = [col, row, vertical, col + row, score]

        new_coordlist = self.sort_coordlist(coordlist, word)

        return new_coordlist

    def sort_coordlist(self, coordlist, word):  # give each coordinate a score, then sort
        new_coordlist = []
        for coord in coordlist:
            col, row, vertical = coord[0], coord[1], coord[2]
            coord[4] = self.check_fit_score(col, row, vertical, word)  # checking scores
            if coord[4]:  # 0 scores are filtered
                new_coordlist.append(coord)
        random.shuffle(new_coordlist)  # randomize coord list; why not?
        new_coordlist.sort(key=lambda i: i[4], reverse=True)  # put the best scores first
        return new_coordlist

    def fit_and_add(self, word):
        # doesn't really check fit except for the first word; otherwise just adds if score is good
        fit = False
        count = 0
        coordlist = self.suggest_coord(word)

        while not fit and count < self.maxloops:

            if len(self.current_word_list) == 0:  # this is the first word: the seed
                # top left seed of longest word yields best results (maybe override)
                vertical = random.randrange(0, 2)
                col = random.randrange(1, self.cols-len(word))
                row = random.randrange(1, self.rows-len(word))
                ''' 
                # optional center seed method, slower and less keyword placement
                if vertical:
                    col = int(round((self.cols + 1)/2, 0))
                    row = int(round((self.rows + 1)/2, 0)) - int(round((word.length + 1)/2, 0))
                else:
                    col = int(round((self.cols + 1)/2, 0)) - int(round((word.length + 1)/2, 0))
                    row = int(round((self.rows + 1)/2, 0))
                # completely random seed method
                col = random.randrange(1, self.cols + 1)
                row = random.randrange(1, self.rows + 1)
                '''

                if self.check_fit_score(col, row, vertical, word):
                    fit = True
                    self.set_word(col, row, vertical, word)
            else:  # a subsquent words have scores calculated
                try:
                    col, row, vertical = coordlist[count][0], coordlist[count][1], coordlist[count][2]
                except IndexError:
                    return  # no more cordinates, stop trying to fit

                if coordlist[count][4]:  # already filtered these out, but double check
                    fit = True
                    self.set_word(col, row, vertical, word)

            count += 1
        return fit

    def check_fit_score(self, col, row, vertical, word):
        '''
        And return score (0 signifies no fit). 1 means a fit, 2+ means a cross.

        The more crosses the better.
        '''
        the_hash = hash((col, row, vertical, word))
        if the_hash not in self.fit_score_cache:
            self.fit_score_cache[the_hash] = self._check_fit_score(col, row, vertical, word)
        return self.fit_score_cache[the_hash]

    def _check_fit_score(self, col, row, vertical, word):
        '''
        And return score (0 signifies no fit). 1 means a fit, 2+ means a cross.

        The more crosses the better.
        '''
        if col < 1 or row < 1:
            return 0

        count, score = 1, 1  # give score a standard value of 1, will override with 0 if collisions detected
        for letter in word.word:
            try:
                active_cell = self.get_cell(col, row)
            except IndexError:
                return 0

            if active_cell == self.empty or active_cell == letter:
                pass
            else:
                return 0

            if active_cell == letter:
                score += 1

            if vertical:
                # check surroundings
                if active_cell != letter:  # don't check surroundings if cross point
                    if not self.check_if_cell_clear(col + 1, row):  # check right cell
                        return 0

                    if not self.check_if_cell_clear(col - 1, row):  # check left cell
                        return 0

                if count == 1:  # check top cell only on first letter
                    if not self.check_if_cell_clear(col, row - 1):
                        return 0

                if count == len(word.word):  # check bottom cell only on last letter
                    if not self.check_if_cell_clear(col, row + 1):
                        return 0
            else:  # else horizontal
                # check surroundings
                if active_cell != letter:  # don't check surroundings if cross point
                    if not self.check_if_cell_clear(col, row - 1):  # check top cell
                        return 0

                    if not self.check_if_cell_clear(col, row + 1):  # check bottom cell
                        return 0

                if count == 1:  # check left cell only on first letter
                    if not self.check_if_cell_clear(col - 1, row):
                        return 0

                if count == len(word.word):  # check right cell only on last letter
                    if not self.check_if_cell_clear(col + 1, row):
                        return 0

            if vertical:  # progress to next letter and position
                row += 1
            else:  # else horizontal
                col += 1

            count += 1

        return score

    def set_word(self, col, row, vertical, word):  # also adds word to word list
        word.col = col
        word.row = row
        word.vertical = vertical
        self.current_word_list.append(word)

        for letter in word.word:
            self.set_cell(col, row, letter)
            if vertical:
                row += 1
            else:
                col += 1

        # Rebuild the letter to loc index and reset the fit score cache:
        self._index_grid_letters()
        self.fit_score_cache = {}

    def set_cell(self, col, row, value):
        self.grid[row - 1][col - 1] = value

    def get_cell(self, col, row):
        return self.grid[row - 1][col - 1]

    def check_if_cell_clear(self, col, row):
        try:
            cell = self.get_cell(col, row)
            if cell == self.empty:
                return True
        except IndexError:
            pass
        return False

    def order_number_words(self):  # orders words and applies numbering system to them
        self.current_word_list.sort(key=lambda i: (i.col + i.row*100))
        count, icount = 1, 1
        for word in self.current_word_list:
            word.number = count
            if icount < len(self.current_word_list):
                if word.col == self.current_word_list[icount].col and word.row == self.current_word_list[icount].row:
                    pass
                else:
                    count += 1
            icount += 1

    def display(self, prune=True):
        """
        Return a dataframe with the empty puzzle. Cells can be one of:
            * '*' - a black cell
            * ' ' - a white (empty) cell
            * number - a cell with a number for a definition
        :param prune: if True, remove all black rows and columns
        :return: A tuple of two DataFrames with the grid: (empty, solved). In the first the cells are empty, only numbers
            are added to it (for definition numbers). The second has the solution in it.
        """
        self.order_number_words()

        new_grid_data = [[self.empty if l==self.empty else ' ' for l in row] for row in self.grid]
        # Replace all letters in the grid with the ' ' character:

        for word in self.current_word_list:
            new_grid_data[word.row - 1][word.col - 1] = word.number
        if self.rtl:
            new_grid = pd.DataFrame([row[::-1] for row in new_grid_data])
            solved_grid = pd.DataFrame([row[::-1] for row in self.grid])
        else:
            new_grid = pd.DataFrame(new_grid_data)
            solved_grid = pd.DataFrame(self.grid)

        if prune:
            # Columns removal:
            cols_to_remove = []
            for col in range(new_grid.shape[1]):
                if (new_grid.iloc[:,col] == '*').all():
                    cols_to_remove.append(col)
            if cols_to_remove:
                new_grid = new_grid.drop(columns=cols_to_remove)
                solved_grid = solved_grid.drop(columns=cols_to_remove)

            # Now the rows:
            rows_to_remove = []
            for row in range(new_grid.shape[0]):
                if (new_grid.iloc[row,:]=='*').all():
                    rows_to_remove.append(row)
            if rows_to_remove:
                new_grid = new_grid.drop(index=rows_to_remove)
                solved_grid = solved_grid.drop(index=rows_to_remove)

        return new_grid.astype(str), solved_grid.astype(str)

    def word_bank(self):
        outStr = ''
        temp_list = duplicate(self.current_word_list)
        random.shuffle(temp_list)  # randomize word list
        for word in temp_list:
            outStr += '%s\n' % word.word
        return outStr

    def legend(self):
        """
        Return the list of across and down definitions
        :return: (across_defs, down_defs)
        """
        down_defs = []
        across_defs = []

        for word in self.current_word_list:
            if word.vertical:
                down_defs.append(f'{word.number}. {word.clue}')
            else:
                across_defs.append(f'{word.number}. {word.clue}')
        return across_defs, down_defs

def _remove_hebrew_end_chars(s):
    # Replace the end hebrew chars with the regular chars
    ends = 'םןףךץ'
    regs = 'מנפכצ'
    trantab = str.maketrans(ends, regs)
    return s.translate(trantab)

def read_word_and_defs(filename=None, data=None, hebrew=True):
    """
    Read the defs and words from a file where each row is {word} | {def}
    :param filename: the name of the text file
    :return:
    """
    if data is None:
        with open(filename, 'r') as fp:
            lines = fp.readlines()
    else:
        lines = data.split('\n')

    res = []
    for line in lines:
        split_line = line.split('|')
        if hebrew:
            res.append((_remove_hebrew_end_chars(split_line[0].strip()), split_line[1].strip()))
        else:
            res.append((split_line[0].strip(), split_line[1].strip()))
    return res


### end class, start execution

if __name__ == '__main__':
    from cw_to_pdf import create_crossword_pdf

    word_list = read_word_and_defs('heb_defs.txt')
    extra_word_list = read_word_and_defs('extra_heb_defs.txt')
    heb_letters = 'אבגדהוזחטיכלמנסעפצקרשת'

    crossword = Crossword(10, 10, '*', 5000, word_list, extra_words=extra_word_list, letters=heb_letters, rtl=True)
    crossword.compute_crossword(time_permitted=5.00, spins=2)
    print(len(crossword.current_word_list), 'out of', len(word_list))

    # Create the PDF:
    # Create a DataFrame from the crossword data
    empty_df, solved_df = crossword.display()

    # Sample definitions
    across_defs, down_defs = crossword.legend()
    across_definitions = ["אופקי"] + across_defs
    down_definitions = ["מאונך"] + down_defs

    # Output PDF file name
    output_filename = "crossword.pdf"

    # Call the function to generate the crossword PDF
    create_crossword_pdf(empty_df, across_definitions, down_definitions, output_filename, solved_df=solved_df)

