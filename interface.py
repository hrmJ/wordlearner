#! /usr/bin/env python
#imports:
import csv
import string
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


#Starting the program
#Load the data:
start()
#Create the main menu {{{1
mainmenuanswers = {'1': 'Create a new wordset',
                   '2': 'View existing wordsets',
                   '3': 'Append to existing wordset',
                   'q': 'quit'}
mainmenu = multimenu('Wordsets:\n',mainmenuanswers)
#Launch the menu {{{1
while True:
    mainmenu.prompt_valid()
    #Quit on q {{{1
    if mainmenu.answer == 'q':
        quit()
        break
    #on 1 create new wlist {{{1
    if mainmenu.answer == '1':
        #ask about the type of the new set
        answers = {'1': 'Singles_set',
                   'h': 'help',
                   'c': 'cancel'}
        wlmenu = multimenu('Give the type of the new set',answers)
        wlmenu.prompt_valid()
        if wlmenu.answer == '1':
            #initialize
            newset = Singles_set()
            #insert the csv data
            newset.createfromcsv()
            print('Succesfully created wordset "{}"'.format(newset.name))
            #update the wordset pickle
            pickle.dump(Wordset.wordsets,open("wordsets.p", "wb"))
            #update the wids pickle
            pickle.dump(Word.wids,open("wids.p", "wb"))
        elif wlmenu.answer == 'h':
            print('Sorry, no help available')
    #on 2 view existing lists {{{1
    if mainmenu.answer == '2':
        #Check if there are wordsets
        if Wordset.wordsets:
            #print the existing ones {{{2
            print('\n'*3)
            print('{0:20} | {1:20} | {2:20} | {3:20} | {4:30} '.format('Name','Type','Creator','languages','Creation date'))
            print('-'*4*26)
            for key, value in Wordset.wordsets.items():
                print('{0:20} | {1:20} | {2:20} | {3:20} | {4:30} '.format(key,value.wstype,value.creator,", ".join(value.languages),value.creationdate))
            print('\n'*3)
        else:
            print('No wordsets created.')
