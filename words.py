#! /usr/bin/env python
#imports:
import os.path
import os
from time import ctime
import glob
from collections import defaultdict
import csv
import codecs
import pickle
from menus import Menu, yesnomenu, multimenu, freemenu
#classes:
#Word
class Word:
    ''' The units that are asked'''
    #list word ids
    wids = list()
    currentwords = dict()
    def __init__(self,language,lemma):
        '''initialize by setting the grade etc'''
        self.grade = 0
        self.timesasked = 0
        self.language = language
        self.lemma = lemma
        # The translations/equivalent/closely related word entries are linked in this dict:
        # It has language codes as keys and lists of word objects as values
        self.linkwords = list()
        #create an id for the word based on the length of the id list
        self.wid = len(Word.wids)
        #if this id already in the list, increment till a unique one will be generated
        while self.wid in Word.wids:
            self.wid += 1
        Word.wids.append(self.wid)
        #How should I arrange the word ids? Are they needed?

    def cardquestion(self):
        """Ask a simple flash card type question"""
        #Set the language to be asked
        os.system('cls' if os.name == 'nt' else 'clear')
        print('-'*20)
        input('{}\n\npress enter to view answers.'.format(self.lemma))
        answers = list()
        for linkid in self.linkwords:
            print(Word.currentwords[linkid].lemma)
        input('Press enter to go to next question')



class Noun(Word):
    pass

class Verb(Word):
    pass

class MixedExpression(Word):
    pass

#Wordset {{{3
class Wordset:
    '''A group of words that can be build on the fly or 
    Created from a csv file or...'''
    wordsets = dict()
    sourcelanguage = ''

    def __init__(self):
        #initialize a list containing word objects
        self.words = dict()
        namemenu = freemenu('Name of the new wordset: ')
        namemenu.prompt()
        #Ask for a valid name until the user gives one
        while namemenu.answer in Wordset.wordsets:
            print("Wordset '{}' already exists. Please give a new one.".format(namemenu.answer))
            namemenu.prompt()
        #insert the set as a new entry in the class dict
        Wordset.wordsets[namemenu.answer] = self
        self.name = namemenu.answer
        #add information about creator and creation date
        self.creator = 'default user'
        self.creationdate = ctime()

    def askone(self):
        """Practice the words in this set"""
        for wid, word in self.words.items():
            if word.language == Wordset.sourcelanguage:
                word.cardquestion()

    def addNewWord(self, newWord, linkWord):
        """Adds a new word to the wordset"""
        self.words[newWord.wid] = newWord
        self.words[linkWord.wid] = linkWord
        newWord.linkwords.append(linkWord.wid)

class Singles_set(Wordset):
    '''A word set that consists of simple word-to-word translation pairs'''

    def createfromcsv(self):
        'put the type name to n attribute'
        self.wstype = 'singles'
        #Ask the user for the path of the csv file
        pathmenu = freemenu('Give the path of the csv file:\n>')
        pathmenu.prompt()
        csvpath = pathmenu.answer
        #Define languages for the csv columns
        langmenu = freemenu('')
        self.languages = list()
        for i in range(1,3):
            langmenu.question = 'Language of column no {}? (ru, fi, en etc)\n>'.format(i)
            langmenu.prompt()
            self.languages.append(langmenu.answer)
        #Read the data from the path
        try:
            with open(csvpath, 'r') as f:
                wordrows = list(csv.reader(f))
        except:
            print('file doesnt exist')
        #iterate throguh all the words in the csv list
        for wordrow in wordrows:
            #Use the third column of csv to get the POS
            if wordrow[2] == 'verb':
                self.addNewWord(Verb(self.languages[0],wordrow[0]),
                                Verb(self.languages[1],wordrow[1])
                                )
            elif wordrow[2] == 'noun':
                self.addNewWord(Noun(self.languages[0],wordrow[0]),
                                Noun(self.languages[1],wordrow[1])
                                )
