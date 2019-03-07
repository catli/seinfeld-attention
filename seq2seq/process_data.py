'''
    Create a dictionary of fasttext embedding, stored locally
    fasttext import. This will hopefully make it easier to load
    and train data.

    This will also be used to store the
    Steps to clean scripts (codify):  
        1) copy direct from website (space-delimited text)  
        2) remove actions in brackets  
        3) change words not in fasttext dictionary like "heeeey" to closest approximation like "heeey", and convert made-up conjuction like "overdie" to "over-die"  
        4) concate the speaker into one string, without space  
        5) create a space between punctuation and words [.,?;!]  
        6) delete apostrophes for shorten words like "it's"

'''
import fastText as ft
import pickle as pk
import os
import re
import pdb



def createLinePairs(corpus):
    '''
        Input: Read episode linse with format:
            ELAINE    Hi    Mr    .    Seinfeld    !
            JERRY    Hey    ,    theres    the    old    man    !
        Output: convert those pairs into array
            [["Hi", "Mr", ".", "Seinfeld", "!"],
            ["Hey", ",", "theres", "the", "old","man","!"]
    '''
    print("Reading lines...")
    # combine every two lines into pairs of vectors
    with open(corpus) as f:
        content = f.readlines()
        print('CONTENT')
        print(content)
    # strip \n and \t, and skip the speaker
    lines = convert_lines_to_arrays(content)

    pairs = []
    for i,x in enumerate(lines[:-1]):
        # create pairs of lines to feed as input and output
        # for model, empty lines represent new scene
        # so any pair wiht an empty line is discarded
        if lines[i] and lines[i+1]: #if neither lines are empty
            pairs.append([lines[i], lines[i+1]])
    return pairs


def convert_lines_to_arrays(content):
    '''
        convert each line in scene to an array of text
        formating when not relevant
    '''
    lines = []
    for x in content:
        line = x.strip()
        if len(line)>0: #skip empty lines
            if 'scene:' in x: #  store empty arrays for new scene
                lines.append([])
            else:
                line_arr = format_line(line)
                if line_arr: # if line not empty
                    lines.append(line_arr)
    return lines

def format_line(line):
    '''
        format the line before storing as an array
    '''
    line = line.lower() # set line to lower case
    line_arr = []
    open_brack = []
    is_dialogue = False
    word = ''
    for s in line:
        if s=="'": # don't store apostrophe, so it's stored as its
            continue
        if s==':': # after first speaker identified
            is_dialogue = True
            continue
        if s=='[': #if open_brack is not null, string is not dialogue
            open_brack.append(s)
            continue
        if s==']': #remove open brack, if closed one found
            open_brack.pop()
            continue
        if is_dialogue and not open_brack: 
            # if not inside bracket and some word to store
            if s == ' ': # if space
                if len(word)>0:
                    line_arr.append(word)
                    word = '' # reset word to blank
            elif re.match("[.,?;!\"]", s):
                # start new word if character
                if len(word)>0:
                    line_arr.append(word)
                    line_arr.append(s)
                    word = ''
            elif re.match("[A-Za-z\-]", s):
                # store if alpha character
                word = word+s
    return line_arr



def line2TrainVector(pairs, word_dict):
    # [TODO] convert each line into vectors
    # don't need to use target lens when not batched
    '''
        Input: Read pairs of lines:
            [["Hi", "Mr", ".", "Seinfeld", "!"],
            ["Hey", ",", "theres", "the", "old","man","!"]

            word_dict is embedding hash formed with processDict() below
        Output: convert into fasttext embedding vectors (dim 300)
            above example returns 
                matrix size 4 x 300 for input
                matrix size 7 x 300 for target
    '''
    input_v = createWordVector(pairs[0], word_dict)
    target_v = createWordVector(pairs[1], word_dict)
    return input_v, target_v


def createWordVector(word_array, word_dict):
    vect = []
    for word in word_array:
        # a hyphenated word may be tricky
        # if cannot find, then may need to split up
        # as 2 word
        if '-' in word and word not in word_dict:
            vect.extend(createHypenEmbed(word))
            continue
        # semi-colons not in fasttext
        if word == ';': word = '.'
        if word == '':
            continue
        if word in word_dict:
            vect.append(word_dict[word])
        else:
            print('NOT IN DICT')
            print(word)
            editted_word = editWord(word, word_dict)
            vect.append(editted_word)
            print(editted_word)
            print(word_array)
    return vect


def editWord(weird_word, word_dict):
    # edit weird string, remove extra letters
    # until word in dict
    last_s = ''
    weird_stack = []
    for i, s in enumerate(weird_word):
        ## create ([index, letter, num]) for each different letter
        if s!=last_s:
            weird_stack.append([i, s, 1])
        else:
            weird_stack[-1][2]+=1 # add 1 to the weird word
        last_s = s
    # sort the stack to find most common group of letters and index
    sorted_stack =  sorted(weird_stack, key = lambda x: x[2])
    most_common = sorted_stack[-1]
    # remove most common letter in the weird word
    # i.e. in heeeeey, remove e
    common_idx = most_common[0]+most_common[2]
    weird_word = weird_word[:(common_idx-1)]+weird_word[common_idx:]
    if weird_word in word_dict:
        return weird_word
    else:
        weird_word = editWord(weird_word, word_dict)
    return weird_word






def createHypenEmbed(word):
    '''
        Handle outlier language with hyphen
    '''
    word_whole = re.sub('-', '', word)
    if word_whole in word_dict:
        return [word_dict[word_whole]]
    else:
        # [TODO] should the hyphenated word be
        # split into two words or kept as an
        # average embedding?
        # currently adding the two word into one vect
        subwords = word.split('-')
        word_vect = [word_dict[subwords[0]]]
        for w in subwords[1:]:
            word_vect.append(word_dict[w])
        return word_vect



class fastDict():

    def __init__(self, read_filename, method):
        # [TODO] allow dynamically init
        self.method = method
        print(method)
        if method == 'store':
            read_filename = '~/FastData/wiki.en/wiki.en.bin'
            print(read_filename)
            self.fast = ft.load_model(
                                os.path.expanduser(read_filename))
        pickle_filename = '~/FastData/wiki.en/wiki.en.pkl'
        self.pickle_path = os.path.expanduser(pickle_filename)
        print(pickle_filename)


    def processDict(self):
        # method = store or import
        # read pickle dictionary
        # if method = store, convert fastText data to pickle format first
        if self.method == 'store':
            self.writeWordDict()
        return self.loadWordDict()


    def loadWordDict(self):
        pickle_reader = open(self.pickle_path, 'rb')
        word_vec = pk.load(pickle_reader)
        return word_vec

    def writeWordDict(self):
        all_words = self.getAllWords()
        self.createWordDict(all_words)


    def getAllWords(self):
        all_the_words = self.fast.get_words()
        return all_the_words

    def createWordDict(self, all_words):
        pickle_writer = open(self.pickle_path, 'wb')
        word_dict = {}
        for word in all_words:
            word_dict[word] = self.fast.get_word_vector(word)
        pk.dump(word_dict, pickle_writer)



if __name__ == '__main__':
    read_filename = '~/FastData/wiki.en/wiki.en.bin'
    method = 'import'
    fast = fastDict(read_filename, method)
    word_dict = fast.processDict()
    # [TODO] clean-up do not need to call these functions in main
    test_filename = '~/Documents/seinfeld/episodes/episode_TheSeinfeldChronicles_copy'
    pairs = createLinePairs(os.path.expanduser(test_filename))
    # [TODO] transfer this into 
    # for pair in pairs: input, output = line2TrainVector(pair, word_dict)
