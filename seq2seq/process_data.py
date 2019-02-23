'''
    Create a dictionary of fasttext embedding, stored locally
    fasttext import. This will hopefully make it easier to load
    and train data.

    This will also be used to store the
'''
import fastText as ft
import pickle as pk
import os
import pdb


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
        pickle_reader = open(self.pickle_path, 'r')
        word_vec = pickle.load(pickle_reader)
        return word_vec

    def writeWordDict(self):
        all_words = self.getAllWords()
        self.createWordDict(all_words)


    def getAllWords(self):
        all_the_words = self.fast.get_words()
        return all_the_words

    def createWordDict(self, all_words):
        pickle_writer = open(self.pickle_path, 'w')
        word_dict = {}
        for word in all_words:
            word_dict[word] = self.fast.get_word_vector(word)
        pk.dump(word, pickle_writer)



if __name__ == '__main__':
    read_filename = '~/FastData/wiki.en/wiki.en.bin'
    method = 'store'
    fast = fastDict(read_filename, method)
    word_dict = fast.processDict()
    pdb.set_trace()
