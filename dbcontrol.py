from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from menus import Menu, yesnomenu, multimenu, freemenu
import datetime

engine = create_engine('sqlite:///words.db', echo=False)
Base = declarative_base()

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

    def __init__(self, insertManually=True):
        """ """
        if insertManually:
            self.lemma = input('Give the lemma of this word: ')
            self.pos = DbWord.posmenu.prompt_valid(definedquestion='Give the part of speech for this word')
            self.language = DbWordset.sourcelang
            self.targetwords.append(TargetWord())
            while DbWord.twordmenu.prompt_valid(definedquestion='Insert target words:') == 'n':
                self.targetwords.append(TargetWord())



class TargetWord(Base):
    """Words that are answers"""
    __tablename__ = "targetwords"
    id = Column(Integer, primary_key=True)
    lemma = Column(String)  
    language = Column(String)  
    pos = Column(String)  
    source_id = Column(Integer, ForeignKey("words.id"))
    DbWordset = relationship("DbWords", backref=backref("targetwords", order_by=id),enable_typechecks=False)

    def __init__(self, insertManually=True):
        """ """
        if insertManually:
            self.lemma = input('Give the lemma of this word: ')
            TargetWord.posmenu
            self.pos = DbWord.posmenu.prompt_valid(definedquestion='Give the part of speech for this word')
            self.language = DbWordset.targetlang


class DbLinkword(Base):
    """For each word, list equivalents"""
    __tablename__ = "linkwords"
 
    id = Column(Integer, primary_key=True)
    #Link this table with the dishes table
    #linkword_id = Column(Integer, ForeignKey("words.id"))
    source = Column(Integer)
    target = Column(Integer)
    priority = Column(Integer)
 
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
        if not DbWordset.sourcelang:
            DbWordset.langmenu.prompt_valid(definedquestion='Select source language')
            DbWordset.sourcelang = DbWordset.langmenu.answer
            DbWordset.langmenu.prompt_valid(definedquestion='Select target language')
            DbWordset.targetlang = DbWordset.langmenu.answer

        self.words.append(DbWord())


class LemmaWordset(DbWordset):
    """" .. """
    def __init__(self,creationdate=datetime.datetime.today(),name='unspecified',creator='unspecified',theme='unspecified',subtheme='unspecified',wstype='Lemmas'):
        super().__init__(name=name,creator=creator,theme=theme,subtheme=subtheme,wstype=wstype,creationdate=creationdate)

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