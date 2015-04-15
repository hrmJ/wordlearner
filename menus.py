#! /usr/bin/env python
#Classes{{{1
#Menu{{{2

class Menu:
    """Any command line menus that are used to ask the user for input"""
    def prompt_valid(self):
            #Make a printable string from the dict:
            options = '\n                '.join("{!s}: {!s}".format(key,val) for (key,val) in sorted(self.validanswers.items()))
            question = "{}\n{}{}\n>".format(self.question,'                ',options)
            self.answer=input(question)
            while self.answer not in self.validanswers.keys():
                self.answer = input("Please give a valid answer.\n {}".format(question))
    def prompt(self):
            #Make a printable string from the dict:
            question = "{}".format(self.question)
            self.answer=input(question)

class yesnomenu(Menu):
    validanswers = { 'y':'yes','n':'no' }

class multimenu(Menu):
    '''Create a menu object that has the possible values listed as a dictionary,
    where the keys represent answers and the values represent explanations of each answer'''
    def __init__(self, question, validanswers):
        self.validanswers=validanswers
        self.question = question

class freemenu(Menu):
    def __init__(self, question):
        self.question = question

