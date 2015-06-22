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
from menus import Menu, yesnomenu, multimenu, freemenu
import datetime
from dbcontrol import SqlaCon, DbWordset, DbWord, TargetWord, LemmaWordset


def quit():
    #update the wordset pickle
    #pickle.dump(Wordset.wordsets,open("wordsets.p", "wb"))
    ##update the wids pickle
    #pickle.dump(Word.wids,open("wids.p", "wb"))
    pass

def start():
    #load the word indexes
    print('Welcome to wordlearner 0.1!\n\n')
    #if os.path.isfile('wids.p'):
    #    Word.wids = pickle.load(open('wids.p', "rb"))
    ##list existing wordsets
    #if os.path.isfile('wordsets.p'):
    #    Wordset.wordsets = pickle.load(open('wordsets.p', "rb"))


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
                       '5': 'Insert words to the current set',
                       '6': 'Inflect words in this set',
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
                   '2': 'Lemmas',
                   'h': 'help',
                   'c': 'cancel'}
        wlmenu = multimenu(answers)
        wlmenu.question = 'Give the type of the new set'
        wlmenu.prompt_valid()
        if wlmenu.answer == '1':
            newset = words.Singles_set()
            newset.createfromcsv()
            print('Succesfully created wordset "{}"'.format(newset.name))
            #update the wordset pickle
            pickle.dump(Wordset.wordsets,open("wordsets.p", "wb"))
            #update the wids pickle
            pickle.dump(Word.wids,open("wids.p", "wb"))
        elif wlmenu.answer == '2':
            con.LoadSession()
            #initialize a list containing word objects
            self.words = dict()
            namemenu = freemenu('Name of the new wordset: ')
            namemenu.prompt()
            #Ask for a valid name until the user gives one
            while con.session.query(DbWordset).filter(DbWordset.name==namemenu.answer).first():
                print("Wordset '{}' already exists. Please give a new one.".format(namemenu.answer))
                namemenu.prompt()
            #insert the set into db
            newset = LemmaWordset(name = namemenu.answer, creationdate = datetime.datetime.today(), creator = 'user x', theme = 'uncategorized')
            #insert words
            inswordmenu = multimenu({'n':'insert a new word','q':'stop inserting'},promptnow='Insert words to the word set')
            while inswordmenu.answer == 'n':
                newset.InsertWord()
                inswordmenu.prompt_valid()
            con.session.add(newset)
            con.session.commit()
            con.session.close()


    def viewsets(self):
        #Check if there are wordsets
        con = SqlaCon()
        con.LoadSession()
        res = con.session.query(DbWordset).all()
        print('\n'*3)
        print('{wsid:3} | {wsname:20} | {wstype:20} | {wscreator:20} | {wscdate:10} | {wstheme:20} | {wssubtheme:20}'.format(wsname='Name',wstype='Type',wscreator='Creator',wscdate='Created',wsid='id',wstheme='Theme', wssubtheme='Subtheme'))
        print('-'*4*30)
        for wset in res:
            print('{wsid:3} | {wsname:20} | {wstype:20} | {wscreator:20} | {wscdate:10} | {wstheme:20} | {wssubtheme:20}'.format(wsname=wset.name,wstype=wset.wstype,wscreator=wset.creator,wscdate=str(wset.creationdate),wsid=wset.id,wstheme=wset.theme, wssubtheme=wset.subtheme))
        self.cursetid = int(input('Select a wordset by id:'))

    def practice(self):
        #testing:
        con.LoadSession()
        ws = con.session.query(LemmaWordset).get(self.cursetid)
        ws.CardLemma()
        #Commit changes:
        con.session.add(ws)
        con.session.commit()
        input('Press enter to continue.')

    def inswords(self):
        """Insert words to the current wordset"""
        con.LoadSession()
        ws = con.session.query(DbWordset).get(self.cursetid)
        inswordmenu = multimenu({'n':'insert next word','q':'stop inserting'},promptnow='Insert words to the current set')
        while inswordmenu.answer == 'n':
            ws.words.append(DbWord())
            inswordmenu.prompt_valid()
        input('Press enter to continue')
        #"""Insert new words to the set"""
        con.session.add(ws)
        con.session.commit()
        con.session.close()

    def inflectwords(self):
        con.LoadSession()
        ws = con.session.query(DbWordset).get(self.cursetid)
        ws.InflectRusVerb()
        con.session.add(ws)
        con.session.commit()
        con.session.close()
        input('Press enter to continue')

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
        elif answer == '5':
            self.inswords()
        elif answer == '6':
            self.inflectwords()


wordmenu = MainMenu()
start()
con = SqlaCon()
while wordmenu.run == True:
    wordmenu.runmenu()
