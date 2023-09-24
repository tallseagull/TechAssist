# Taken from here: https://github.com/jeremy886/crossword_helmig/blob/master/crossword_puzzle.py
import random, re, time, string
from copy import copy as duplicate
import pandas as pd
from cw_to_pdf import create_crossword_pdf


class Crossword(object):
    def __init__(self, cols, rows, empty='-', maxloops=2000, available_words=None, extra_words=None, letters=None,
                 rtl=False):
        self.cols = cols
        self.rows = rows
        self.empty = empty
        self.maxloops = maxloops
        self.available_words = available_words if available_words is not None else []
        self.extra_words = extra_words if extra_words is not None else []
        self.randomize_word_list()
        self.rtl = rtl  # Is this right to left? (e.g. hebrew)

        self.current_word_list = []
        self.debug = 0

        if letters is None:
            self.letters = string.ascii_lowercase
        else:
            self.letters = letters

        self.clear_grid()

    def clear_grid(self):  # initialize grid and fill with empty character
        self.grid = []
        for i in range(self.rows):
            ea_row = []
            for j in range(self.cols):
                ea_row.append(self.empty)
            self.grid.append(ea_row)

    def _randomize_word_list_ord(self, words_in):  # also resets words and sorts by length
        temp_list = []
        for word in words_in:
            if isinstance(word, Word):
                temp_list.append(Word(word.word, word.clue))
            else:
                temp_list.append(Word(word[0], word[1]))
        random.shuffle(temp_list)  # randomize word list
        temp_list.sort(key=lambda i: len(i.word), reverse=True)  # sort by length
        return temp_list

    def randomize_word_list(self):  # also resets words and sorts by length
        self.available_words = self._randomize_word_list_ord(self.available_words)
        self.extra_words = self._randomize_word_list_ord(self.extra_words)

    def compute_crossword(self, time_permitted=5.00, spins=3):
        time_permitted = float(time_permitted)

        count = 0
        copy = Crossword(self.cols, self.rows, self.empty, self.maxloops, self.available_words, self.extra_words,
                         self.letters, self.rtl)

        start_full = float(time.time())
        while (float(time.time()) - start_full) < time_permitted or count == 0:  # only run for x seconds
            self.debug += 1
            copy.current_word_list = []
            copy.clear_grid()
            copy.randomize_word_list()
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
                        break

            # buffer the best crossword by comparing placed words
            if len(copy.current_word_list) > len(self.current_word_list):
                self.current_word_list = copy.current_word_list
                self.grid = copy.grid
            count += 1
        return

    def suggest_coord(self, word):
        count = 0
        coordlist = []
        glc = -1
        for given_letter in word.word:  # cycle through letters in word
            glc += 1
            rowc = 0
            for row in self.grid:  # cycle through rows
                rowc += 1
                colc = 0
                for cell in row:  # cycle through  letters in rows
                    colc += 1
                    if given_letter == cell:  # check match letter in word to letters in row
                        try:  # suggest vertical placement
                            if rowc - glc > 0:  # make sure we're not suggesting a starting point off the grid
                                if ((rowc - glc) + word.length) <= self.rows:  # make sure word doesn't go off of grid
                                    coordlist.append([colc, rowc - glc, 1, colc + (rowc - glc), 0])
                        except:
                            pass
                        try:  # suggest horizontal placement
                            if colc - glc > 0:  # make sure we're not suggesting a starting point off the grid
                                if ((colc - glc) + word.length) <= self.cols:  # make sure word doesn't go off of grid
                                    coordlist.append([colc - glc, rowc, 0, rowc + (colc - glc), 0])
                        except:
                            pass
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

    def fit_and_add(self,
                    word):  # doesn't really check fit except for the first word; otherwise just adds if score is good
        fit = False
        count = 0
        coordlist = self.suggest_coord(word)

        while not fit and count < self.maxloops:

            if len(self.current_word_list) == 0:  # this is the first word: the seed
                # top left seed of longest word yields best results (maybe override)
                vertical, col, row = random.randrange(0, 2), 1, 1
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
                    self.set_word(col, row, vertical, word, force=True)
            else:  # a subsquent words have scores calculated
                try:
                    col, row, vertical = coordlist[count][0], coordlist[count][1], coordlist[count][2]
                except IndexError:
                    return  # no more cordinates, stop trying to fit

                if coordlist[count][4]:  # already filtered these out, but double check
                    fit = True
                    self.set_word(col, row, vertical, word, force=True)

            count += 1
        return fit

    def check_fit_score(self, col, row, vertical, word):
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

    def set_word(self, col, row, vertical, word, force=False):  # also adds word to word list
        if force:
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
        return

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

    def solution(self):  # return solution grid
        if self.rtl:
            new_grid = pd.DataFrame([row[::-1] for row in self.grid])
        else:
            new_grid = pd.DataFrame(self.grid)
        return new_grid

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
        :return: A DataFrame with the grid
        """
        self.order_number_words()

        new_grid_data = [[self.empty if l==self.empty else ' ' for l in row] for row in self.grid]
        # Replace all letters in the grid with the ' ' character:

        for word in self.current_word_list:
            new_grid_data[word.row - 1][word.col - 1] = word.number
            # self.set_cell(word.col, word.row, word.number)
        if self.rtl:
            new_grid = pd.DataFrame([row[::-1] for row in new_grid_data])
        else:
            new_grid = pd.DataFrame(new_grid_data)

        if prune:
            # Columns removal:
            cols_to_remove = []
            for col in range(new_grid.shape[1]):
                if (new_grid.iloc[:,col] == '*').all():
                    cols_to_remove.append(col)
            if cols_to_remove:
                new_grid = new_grid.drop(columns=cols_to_remove)

            # Now the rows:
            rows_to_remove = []
            for row in range(new_grid.shape[0]):
                if (new_grid.iloc[row,:]=='*').all():
                    rows_to_remove.append(row)
            if rows_to_remove:
                new_grid = new_grid.drop(index=rows_to_remove)
                
        return new_grid.astype(str)

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
            down_across = word.down_across()
            if word.vertical:
                down_defs.append(f' {word.number}. {word.clue} ')
            else:
                across_defs.append(f' {word.number}. {word.clue} ')
        return across_defs, down_defs


class Word(object):
    def __init__(self, word=None, clue=None):
        self.word = re.sub(r'\s', '', word.lower())
        self.clue = clue
        self.length = len(self.word)
        # the below are set when placed on board
        self.row = None
        self.col = None
        self.vertical = None
        self.number = None

    def down_across(self):  # return down or across
        if self.vertical:
            return 'down'
        else:
            return 'across'

    def __repr__(self):
        return self.word

def _remove_hebrew_end_chars(s):
    # Replace the end hebrew chars with the regular chars
    ends = 'םןףךץ'
    regs = 'מנפכצ'
    trantab = str.maketrans(ends, regs)
    return s.translate(trantab)

def read_word_and_defs(filename, hebrew=True):
    """
    Read the defs and words from a file where each row is {word} | {def}
    :param filename: the name of the text file
    :return:
    """
    with open(filename, 'r') as fp:
        lines = fp.readlines()

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

    # word_list = ['saffron', 'The dried, orange yellow plant used to as dye and as a cooking spice.'], \
    #             ['pumpernickel', 'Dark, sour bread made from coarse ground rye.'], \
    #             ['leaven', 'An agent, such as yeast, that cause batter or dough to rise..'], \
    #             ['coda', 'Musical conclusion of a movement or composition.'], \
    #             ['paladin', 'A heroic champion or paragon of chivalry.'], \
    #             ['syncopation', 'Shifting the emphasis of a beat to the normally weak beat.'], \
    #             ['albatross', 'A large bird of the ocean having a hooked beek and long, narrow wings.'], \
    #             ['harp', 'Musical instrument with 46 or more open strings played by plucking.'], \
    #             ['piston',
    #              'A solid cylinder or disk that fits snugly in a larger cylinder and moves under pressure as in an engine.'], \
    #             ['caramel', 'A smooth chery candy made from suger, butter, cream or milk with flavoring.'], \
    #             ['coral', 'A rock-like deposit of organism skeletons that make up reefs.'], \
    #             ['dawn', 'The time of each morning at which daylight begins.'], \
    #             ['pitch', 'A resin derived from the sap of various pine trees.'], \
    #             ['fjord', 'A long, narrow, deep inlet of the sea between steep slopes.'], \
    #             ['lip', 'Either of two fleshy folds surrounding the mouth.'], \
    #             ['lime', 'The egg-shaped citrus fruit having a green coloring and acidic juice.'], \
    #             ['mist', 'A mass of fine water droplets in the air near or in contact with the ground.'], \
    #             ['plague', 'A widespread affliction or calamity.'], \
    #             ['yarn', 'A strand of twisted threads or a long elaborate narrative.'], \
    #             ['snicker', 'A snide, slightly stifled laugh.']

    word_list = read_word_and_defs('heb_defs.txt')
    extra_word_list = read_word_and_defs('extra_heb_defs.txt')
    heb_letters = 'אבגדהוזחטיכלמנסעפצקרשת'

    a = Crossword(13, 13, '*', 5000, word_list, extra_words=extra_word_list, letters=heb_letters, rtl=True)
    a.compute_crossword(2)
    print(a.word_bank())
    print(a.solution())
    # print(a.word_find())
    print(a.display())
    print(a.legend())
    print(len(a.current_word_list), 'out of', len(word_list))

    # Create the PDF:
    # Sample definitions
    across_defs, down_defs = a.legend()
    across_definitions = ["אופקי"] + across_defs
    down_definitions = ["מאונך"] + down_defs

    # Create a DataFrame from the crossword data
    df = a.display()

    # Output PDF file name
    output_filename = "crossword.pdf"

    # Call the function to generate the crossword PDF
    create_crossword_pdf(df, across_definitions, down_definitions, output_filename)

