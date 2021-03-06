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
from dbcontrol import SqlaCon, DbWordset, DbWord, TargetWord, LemmaWordset, LemmaMeta, InflMeta, GenMeta
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import and_, or_, between

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
                       '3': 'View words in this set',
                       '4': 'Practice',
                       '5': 'Insert words to the current set',
                       '6': 'Inflect words in this set',
                       '7': 'Edit words in this set',
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


    def printset(self):
        """print the words in the set"""
        #Clear the terminal:
        os.system('cls' if os.name == 'nt' else 'clear')
        #Load sqlalchemy session and pick the current wordset
        con.LoadSession()
        ws = con.session.query(LemmaWordset).get(self.cursetid)
        ws.printWords()
        input('Press enter to continue')


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
        """Pick a practice type and select filters. Then practice the current wordset"""
        #Load sqlalchemy session and pick the current wordset
        con.LoadSession()
        ws = con.session.query(LemmaWordset).get(self.cursetid)
        # Choose question type and filters
        pickptype = multimenu({'1':'Flash cards about lemmas','2':'Russian inflection practice'},promptnow='Choose practice type')
        self.pickfilter = multimenu({'g':'by grade','w':'By times answered wrong','t':'by times practiced','n':'do not filter'},promptnow='Do you want to filter the words that will be asked?')
        ws.questiontype = SetQuestionType(pickptype.answer)
        self.evaluatePracticeFilter(con.session,ws)
        #Choose the number of words to practice and run the practice method
        picknumber = input('(After applying the filters) this word set contains {} source word entries. How many would you like to practice?\n>'.format(len(ws.allowedids)))
        ws.Practice(int(picknumber))
        #Commit changes:
        con.session.add(ws)
        con.session.commit()
        input('Press enter to continue.')

    def evaluatePracticeFilter(self,session,ws):
        """Do the actual filtering"""
        subquery = session.query(DbWord.id).filter(DbWord.wordset_id==self.cursetid).subquery()
        attribute = VerbalizeFilterAnswer(self.pickfilter.answer)
        if self.pickfilter.answer == 't':
            allowedids = DefineMinMax(subquery,session,GenMeta, attribute)
        elif ws.questiontype == 'cardlemma':
            allowedids = DefineMinMax(subquery,session,LemmaMeta, attribute)
        elif ws.questiontype == 'rusInflect':
            allowedids = DefineMinMax(subquery,session,InflMeta, attribute)
        elif self.pickfilter.answer =='n':
            allowedids = session.query(DbWord.id).with_parent(ws).all()
        #Flatten:
        allowedids = list(zip(*allowedids))
        ws.allowedids = allowedids[0]


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
        ws.InflectRus()
        con.session.add(ws)
        con.session.commit()
        con.session.close()
        input('Press enter to continue')

    def EditWords(self):
        """Edit wirds in This set"""
        con.LoadSession()
        ws = con.session.query(DbWordset).get(self.cursetid)
        worddict = dict()
        for idx, word in enumerate(ws.words):
            worddict[str(idx)] = word.lemma
        editmenu = multimenu(validanswers=worddict, promptnow='Choose the word to edit:')
        editedword = ws.words[int(editmenu.answer)]
        if multimenu(validanswers={'y':'yes','n':'no'}, promptnow='Edit source word?') == 'y':
            editedword.lemma = input('Replace {} with:'.format(editedword.lemma))
        for targetword in editedword.targetwords:
            targetmenu = multimenu(validanswers={'d':'delete','e':'edit', 'c': 'Leave as is'}, promptnow='What shall I do with {}'.format(targetword.lemma))
            if targetmenu.answer == 'd':
                editedword.targetwords
            elif targetmenu.answer == 'e':
                targetword.lemma = input('Replace {} with:'.format(targetword.lemma))
        #Commit changes:
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
        elif answer == '3':
            self.printset()
        elif answer == '4':
            self.practice()
        elif answer == '5':
            self.inswords()
        elif answer == '6':
            self.inflectwords()
        elif answer == '7':
            self.EditWords()

################################################################################
def DefineMinMax(subquery, session, category, attribute):
    """Ask the user for min/max. First find current border values by querying the database"""
    idcat = getattr(category,'word_id')
    attributecat =  getattr(category, attribute)
    lowest = session.query(func.min(attributecat)).filter(idcat.in_(subquery)).first()
    highest = session.query(func.max(attributecat)).filter(idcat.in_(subquery)).first()
    mingrade = int(input('Give the lowest {} allowed (from {} to {})\n>'.format(attribute, lowest[0],highest[0])))
    maxgrade = int(input('Give the highest {} allowed (from {} to {})\n>'.format(attribute, lowest[0],highest[0])))
    subq2 = session.query(idcat).filter(and_(idcat.in_(subquery),attributecat.between(mingrade,maxgrade)))
    res = session.query(DbWord.id).filter(DbWord.id.in_(subq2))
    return res.all()

def VerbalizeFilterAnswer(answer):
    """simplify the code by making this a separate function"""
    if answer =='g':
        return  'grade'
    elif answer =='w':
        return 'wrong'
    elif answer =='t':
        return 'practicetimes'

def SetQuestionType(answer):
    """simplify the code by making this a separate function"""
    if answer == '1':
            return  'cardlemma'
    elif answer == '2':
            return  'rusInflect'

################################################################################

wordmenu = MainMenu()
start()
con = SqlaCon()
while wordmenu.run == True:
    wordmenu.runmenu()
