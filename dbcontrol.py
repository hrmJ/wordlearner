from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from menus import Menu, yesnomenu, multimenu, freemenu
from termcolor import colored
import datetime
import os
from wiktionary import RusVerb

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
                    infldict = RusVerb(word.lemma)
                for form, value in infldict.items():
                    word.inflection.append(Inflection(form,value,1))

class LemmaWordset(DbWordset):
    """" .. """
    def __init__(self,creationdate=datetime.datetime.today(),name='unspecified',creator='unspecified',theme='unspecified',subtheme='unspecified',wstype='Lemmas'):
        super().__init__(name=name,creator=creator,theme=theme,subtheme=subtheme,wstype=wstype,creationdate=creationdate)

    def CardLemma(self):
        """Practice lemmas with basic flashcard questions"""
        practmenu = yesnomenu()
        for word in self.words:
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


#class Declination(Base):
#    """For nouns, list the declination in a separate db table"""
    #__tablename__ = "declination"
 
    #id = Column(Integer, primary_key=True)
    #name = Column(String)  
    #iclass = Column(String)
    #dish = relationship("Dish", backref=backref("ingredients", order_by=id))
 
#class Conjugation(Base):
#    """For verbs, list the conjugation in a separate db table"""
#    __tablename__ = "conjugation"
# 
#    id = Column(Integer, primary_key=True)
#    name = Column(String)  
#    # If you want to clssify ingerdients some way
#    iclass = Column(String)
#    # Price is also optional
#    price = Column(Float)
#    #Link this table with the dishes table
#    dish_id = Column(Integer, ForeignKey("dishes.id"))
#    dish = relationship("Dish", backref=backref("ingredients", order_by=id))

# create tables
Base.metadata.create_all(engine)
