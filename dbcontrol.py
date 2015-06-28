from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from menus import Menu, yesnomenu, multimenu, freemenu
from termcolor import colored
import datetime
import os
from wiktionary import RusVerb
import random

engine = create_engine('sqlite:///words.db', echo=False)
Base = declarative_base()

#### Database tables########################################

class GenMeta(Base):
    """Information about how often and when practiced as lemmas"""
    __tablename__ = "genmeta"
    id = Column(Integer, primary_key=True)
    last_practiced = Column(Date)
    practicetimes = Column(Integer)
    word_id = Column(Integer, ForeignKey('words.id'))

    def __init__(self):
        """ """
        self.last_practiced = datetime.datetime.today()
        self.practicetimes = 0

class LemmaMeta(Base):
    """Information about how often and when practiced as lemmas"""
    __tablename__ = "lemmameta"
    id = Column(Integer, primary_key=True)
    grade = Column (Integer)
    wrong = Column(Integer)
    right = Column(Integer)
    word_id = Column(Integer, ForeignKey('words.id'))

    def __init__(self):
        """ """
        self.grade = 0
        self.wrong = 0
        self.right = 0

class InflMeta(Base):
    """Information about how often and when practiced as inflections"""
    __tablename__ = "inflmeta"
    id = Column(Integer, primary_key=True)
    grade = Column (Integer)
    wrong = Column(Integer)
    right = Column(Integer)
    word_id = Column(Integer, ForeignKey('words.id'))

    def __init__(self, insertManually=True):
        """ """
        self.grade = 0
        self.wrong = 0
        self.right = 0

class TargetWord(Base):
    """Words that are answers"""
    __tablename__ = "targetwords"
    id = Column(Integer, primary_key=True)
    lemma = Column(String)  
    language = Column(String)  
    pos = Column(String)  
    source_id = Column(Integer, ForeignKey("words.id"))
    DbWord = relationship("DbWord", backref=backref("targetwords", order_by=id),enable_typechecks=False)
    comment = Column(String)

    def __init__(self, insertManually=True):
        """ """
        if insertManually:
            self.lemma = input('Give the lemma of this word: ')
            self.pos = DbWord.posmenu.prompt_valid(definedquestion='Give the part of speech for this word')
            self.language = DbWordset.targetlang

    def AskRusConj(self):
        """Make a question about this word's conjugation
        - For every uncorrect stress give 0,5 minus point
        - For every uncorrect answer give 1 minus point
        - if <= minus points, consider correct 
        """
        print('{0}\n{1}{2}'.format(self.lemma,'='*len(self.lemma),'\n'*2))
        askedforms = ('s1pres','s3pres','p3pres','simp')
        askedvalues = pickValues(self.inflection,'form',askedforms)
        minuspoints = 0
        for askedvalue in askedvalues:
            answer = input(askedvalue.form + ': ')
            while answer == answer.lower():
                answer = input('Please indicate the stress with a capital letter!\n' + askedvalue.form + ': ')
            if answer != UcaseStress(askedvalue.value,askedvalue.stress):
                #If the user didn't give the exact right answer with the right stress
                if answer.lower() == askedvalue.value.lower():
                    #If only the stress was wrong
                    minuspoints += 0.5
                    print('The answer was correct, but you got the stress wrong.')
                else:
                    #If the word wasn't right, either
                    print('Sorry, wrong answer.')
                    minuspoints += 1
                input('The correct answer is: ' + ColorStress(askedvalue.value,askedvalue.stress))
            else:
                print('Correct!')
        input('Minus points for this word: {}\n===========================\n(press enter to continue)'.format(minuspoints))
        return minuspoints


class DbWord(Base):
    """The table that includes all the words"""
    __tablename__ = "words"
 
    id = Column(Integer, primary_key=True)
    lemma = Column(String)  
    language = Column(String)  
    pos = Column(String)  
    wordset_id = Column(Integer, ForeignKey("wordsets.id"))
    DbWordset = relationship("DbWordset", backref=backref("words", order_by=id),enable_typechecks=False)
    posmenu = multimenu({'N':'Noun','V':'Verb','Adv':'Adverb','A':'Adjective'})
    twordmenu = multimenu({'n':'Insert next target word','q':'Stop inserting targetwords'})
    #Metadata for different practice types (grades etc)
    genmeta = relationship("GenMeta", uselist=False, backref="words")
    lemmameta = relationship("LemmaMeta", uselist=False, backref="words")
    inflmeta = relationship("InflMeta", uselist=False, backref="words")

    def __init__(self, insertManually=True):
        """ Insert a new word"""
        if not DbWordset.sourcelang or not DbWordset.targetlang:
            setSourceLang()
        if insertManually:
            self.lemma = input('Give the lemma of this word: ')
            self.pos = DbWord.posmenu.prompt_valid(definedquestion='Give the part of speech for this word')
            self.language = DbWordset.sourcelang
            #Initialize the metadata tables
            self.lemmameta = LemmaMeta()
            self.genmeta = GenMeta()
            self.inflmeta = InflMeta()
            #Set target words
            while DbWord.twordmenu.prompt_valid(definedquestion='Insert target words:') == 'n':
                self.targetwords.append(TargetWord())

    def PrintTargetWords(self):
        """Print all the target words of this source word"""
        #print answers
        print('\n'*2 + '='*50 + '\n')
        for tword in self.targetwords:
            print(tword.lemma + '\n')
        print('='*50 + '\n')
        input('press enter to continue.')

    def WriteGenMeta(self):
        """Write general metainformation every time a word is practiced"""
        self.genmeta.last_practiced = datetime.datetime.today()
        self.genmeta.practicetimes += 1

class DbWordset(Base):
    """ Words are organized in sets"""
    # DB table
    __tablename__ = "wordsets"
    id = Column(Integer, primary_key=True)
    name = Column(String,default='unspecified')
    creator = Column(String,default='unspecified')
    creationdate = Column(Date)
    theme = Column(String,default='unspecified')
    subtheme = Column(String,default='unspecified')
    wstype = Column(String,default='unspecified')
    sourcelang = ''
    targetlang = ''
    langmenu = multimenu({'fi':'Finnish','ru':'Russian','en':'English'})
    #--------------------
    currentset = False

    def __init__(self,creationdate=datetime.datetime.today(),name='unspecified',creator='unspecified',theme='unspecified',subtheme='unspecified',wstype='unspecified'):
        self.name = name
        self.creator = creator
        self.creationdate = creationdate
        self.theme = theme
        self.subtheme = subtheme
        self.wstype = wstype
        DbWordset.currentset = self

    def InsertWord(self):
        """Insert new words to the set"""
        if not DbWordset.sourcelang or not DbWordset.targetlang:
            setSourceLang()
        self.words.append(DbWord())

    def InflectRusVerb(self):
        """Inflect all the verbs in a Russian wordset"""
        for sourceword in self.words:
            for word in sourceword.targetwords:
                if word.pos == 'V':
                    #Fetch inflection information from wiktionary:
                    infldict = RusVerb(word.lemma)
                    for form, value in infldict.items():
                        stresslist = MarkStress(value)
                        word.inflection.append(Inflection(form,stresslist[0],stresslist[1]))

    def collectWordsToAsk(self,wordcount):
        """Make a list of words that will be asked in one way or another"""
        self.wordstoask = list()
        #1. Collect all the words that can be used in this question type
        if self.questiontype == 'rusConjug':
            #for certain types, use the target words
            for sourceword in self.words:
                takethisword = True
                for word in sourceword.targetwords:
                    if not self.EvalueateWordForQuestion(word):
                        takethisword = False
                if takethisword and sourceword.id in self.allowedids:
                    #if all the target words matched the condition, take this word
                    self.wordstoask.append(sourceword)
        if self.questiontype == 'cardlemma':
            #For other types, use the source words
            for word in self.words:
                if self.EvalueateWordForQuestion(word) and word.id in self.allowedids:
                    #if the source word matches the condition, take this word
                    self.wordstoask.append(word)
        #2. Limit the number of asked words and shuffle
        if wordcount>len(self.wordstoask):
            wordcount = len(self.wordstoask)
        self.wordstoask = random.sample(self.wordstoask,wordcount)


    def EvalueateWordForQuestion(self,word):
        """"""
        #Conjugation test for Russian verbs
        if self.questiontype == 'rusConjug':
            if word.pos == 'V':
                return True
        if self.questiontype == 'cardlemma':
            return True
        #If no condition matches, return false
        return False

class LemmaWordset(DbWordset):
    """" .. """
    def __init__(self,creationdate=datetime.datetime.today(),name='unspecified',creator='unspecified',theme='unspecified',subtheme='unspecified',wstype='Lemmas'):
        super().__init__(name=name,creator=creator,theme=theme,subtheme=subtheme,wstype=wstype,creationdate=creationdate)

    def CardLemma(self,wordcount=10):
        """Practice lemmas with basic flashcard questions"""
        practmenu = yesnomenu()
        self.collectWordsToAsk(wordcount)
        for word in self.wordstoask:
            os.system('cls' if os.name == 'nt' else 'clear')
            practmenu.question=('Do you know {} in tl?'.format(colored(word.lemma,'red')))
            word.WriteGenMeta()
            if practmenu.prompt_valid() == 'y':
                word.lemmameta.grade += 1
                word.lemmameta.right += 1
            else:
                word.lemmameta.grade -= 1
                word.lemmameta.wrong += 1
            word.PrintTargetWords()

    def ConjugationPractice(self,wordcount):
        """Questions based on the information about verbs' conjugation
        """
        self.collectWordsToAsk(wordcount)
        for word in self.wordstoask:
            for targetword in word.targetwords:
                os.system('cls' if os.name == 'nt' else 'clear')
                inflpoints = targetword.AskRusConj()
                word.WriteGenMeta()
                if inflpoints >= 1:
                    word.inflmeta.grade -= 1
                    word.inflmeta.wrong += 1
                else:
                    word.inflmeta.grade += 1
                    word.inflmeta.right += 1

class Inflection(Base):
    """Contains word forms"""
    __tablename__ = "inflection"
    id = Column(Integer, primary_key=True)
    form = Column(String)
    value = Column(String)
    stress = Column(Integer)
    lemma_id = Column(Integer, ForeignKey("targetwords.id"))
    TargetWord = relationship("TargetWord", backref=backref("inflection", order_by=id),enable_typechecks=False)

    def __init__(self,form,value,stress):
        self.form = form
        self.value = value
        self.stress = stress

###### functions ######################################################

def WriteLemmaMeta(thisWord):
    """Write information about right or wrong answers to database"""
    This
    pass

def MarkStress(word):
    """find stress, unaccent the vowel and mark the number"""
    vowels = {'а́':'а','о́':'о','е́':'е','у́':'у','и́':'и','ы́':'ы','э́':'э','ю́':'ю','я́':'я','ё':'ё'}
    for stressedvowel, unstressedvowel in vowels.items():
        if stressedvowel in word.lower():
            stressidx = word.find(stressedvowel)
            word = word.replace(stressedvowel,unstressedvowel)
            #return a list with the word as first value and stressidx as second
            return [word,stressidx]

def pickValues(olist, attr, values):
    """Input a list of objects. Pick all that have a value that is found in the 'values' list"""
    returnlist = list()
    for o in olist:
        if getattr(o,attr) in values:
            returnlist.append(o)
    return returnlist

def ColorStress(word, letter):
    return ''.join([word[:letter], colored(word[letter],'red'),  word[letter+1:]])

def UcaseStress(word, letter):
    return ''.join([word[:letter], word[letter].upper(),  word[letter+1:]])

###### other ######################################################

class SqlaCon:
    """Autoconn:ct to sqlite via sqlalchemy"""

    def __init__(self):
        self.Base = Base
        self.engine = engine

    def LoadSession(self):
        """"""
        metadata = self.Base.metadata
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def insert(self, dbobj):
        """Insert via sqla"""
        self.LoadSession()
        self.session.add(dbobj)
        self.session.commit()

def setSourceLang():
    """set the language parametres"""
    DbWordset.langmenu.prompt_valid(definedquestion='Select source language')
    DbWordset.sourcelang = DbWordset.langmenu.answer
    DbWordset.langmenu.prompt_valid(definedquestion='Select target language')
    DbWordset.targetlang = DbWordset.langmenu.answer

Base.metadata.create_all(engine)
