#! /usr/bin/env python
#imports:
import csv
import string
import os
import sys
import codecs
import pickle
import os.path
import glob
from menus import Menu, yesnomenu, multimenu
from words import Word, Wordset, Singles_set


def quit():
    #update the wordset pickle
    pickle.dump(Wordset.wordsets,open("wordsets.p", "wb"))
    #update the wids pickle
    pickle.dump(Word.wids,open("wids.p", "wb"))

def start():
    #load the word indexes
    print('Welcome to wordlearner 0.1!\n\n')
    if os.path.isfile('wids.p'):
        Word.wids = pickle.load(open('wids.p', "rb"))
    #list existing wordsets
    if os.path.isfile('wordsets.p'):
        Wordset.wordsets = pickle.load(open('wordsets.p', "rb"))


class options:
    """User-defined parameters"""

    pass

class MainMenu:
    """This class includes all
    the comand line menu options and actions"""
    mainanswers = {    '1': 'Create a new wordset',
                       '2': 'View existing wordsets',
                       '3': 'Append to existing wordset',
                       '4': 'Practice',
                       'q': 'quit'}

    def __init__(self):
        self.menu = multimenu(MainMenu.mainanswers)
        # Selectable options:
        self.selectedwordset = 'none'
        self.selecteddb = 'none'
        #Control the program flow
        self.run = True

    def runmenu(self):
        'Run the main menu'
        #Clear the terminal:
        os.system('cls' if os.name == 'nt' else 'clear')
        #Build the selected options
        self.menu.question = 'Welcome\n\n' + '-'*20 + \
                          '''\n\nSelected options: 
                             \nWordset: {}\n {}
                             '''.format(self.selectedwordset,'\n'*2 + '-'*20 + '\n'*2)
        self.menu.validanswers = MainMenu.mainanswers
        self.menu.prompt_valid()
        self.MenuChooser(self.menu.answer)
        #Show language if selected:


    def createset(self):
        #ask about the type of the new set
        answers = {'1': 'Singles_set',
                   'h': 'help',
                   'c': 'cancel'}
        wlmenu = multimenu(answers)
        wlmenu.question = 'Give the type of the new set'
        wlmenu.prompt_valid()
        if wlmenu.answer == '1':
            newset = Singles_set()
            newset.createfromcsv()
            print('Succesfully created wordset "{}"'.format(newset.name))
            #update the wordset pickle
            pickle.dump(Wordset.wordsets,open("wordsets.p", "wb"))
            #update the wids pickle
            pickle.dump(Word.wids,open("wids.p", "wb"))

    def viewsets(self):
        #Check if there are wordsets
        if Wordset.wordsets:
            #print the existing ones {{{2
            print('\n'*3)
            print('{5:3} | {0:20} | {1:20} | {2:20} | {3:20} | {4:30} '.format('Name','Type','Creator','languages','Creation date','id'))
            print('-'*4*26)
            #To make it easier to select a wordset by number
            wordsetid = 1
            wordsetkeys = dict()
            for key, value in Wordset.wordsets.items():
                wordsetkeys[str(wordsetid)] = key
                print('{5:3} | {0:20} | {1:20} | {2:20} | {3:20} | {4:30} '.format(key,value.wstype,value.creator,", ".join(value.languages),value.creationdate, wordsetid))
                wordsetid += 1
            print('\n'*3)
            self.selectedwordset = wordsetkeys[str(input('Write the id of the wordset you want to use:'))]
            Word.currentwords = Wordset.wordsets[self.selectedwordset].words
        else:
            print('No wordsets created.')

    def practice(self):
        #testing:
        Wordset.sourcelanguage = 'fi'
        Wordset.wordsets[self.selectedwordset].askone()
        input('Press enter to continue.')

    def MenuChooser(self,answer):
        if answer == 'q':
            self.run = False
            quit()
        elif answer == '1':
            self.createset()
        elif answer == '2':
            self.viewsets()
        elif answer == '4':
            self.practice()


wordmenu = MainMenu()
start()
while wordmenu.run == True:
    wordmenu.runmenu()
