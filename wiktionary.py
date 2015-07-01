from bs4 import BeautifulSoup
from urllib import request


def GetPage(wordstring = 'лазить'):
    """Get wiktionary page object for parsing"""
    word = request.quote(wordstring.encode('utf-8'))
    address = "http://ru.wiktionary.org/wiki/" + word
    wikipage = request.urlopen(address)
    wphtml = wikipage.read()
    wikipage.close()
    return wphtml

def RusVerb(lemma):
    """Fetch information about inflection for Russian verbs"""
    page = GetPage(lemma)
    soup = BeautifulSoup(page)

    #Get the * table (it includes the paradigm)
    table = soup.find('table',attrs={'cellpadding':'2'})
    rows = table.find_all('tr')

    infldict = {}
    #present tense
    infldict["s1pres"] = rows[1].find_all('td')[1].contents[0]
    infldict["s2pres"] = rows[2].find_all('td')[1].contents[0]
    infldict["s3pres"] = rows[3].find_all('td')[1].contents[0]
    infldict["p1pres"] = rows[4].find_all('td')[1].contents[0]
    infldict["p2pres"] = rows[5].find_all('td')[1].contents[0]
    infldict["p3pres"] = rows[6].find_all('td')[1].contents[0]
    #past tense
    infldict["spastmasc"] = rows[3].find_all('td')[2].contents[0]
    infldict["spastfem"] = rows[3].find_all('td')[2].contents[2].strip()
    infldict["ppast"] = rows[4].find_all('td')[2].contents[0]
    #imperative mode
    infldict["simp"] = rows[2].find_all('td')[3].contents[0]
    return infldict

def RusNoun(lemma):
    """Fetch information about inflection for Russian Nouns"""
    #Check for A+ N
    splitted = lemma.split()
    if len(splitted)>1 and  splitted[0][-2:] in ('ый','ой','ая','ое','ий','яя','ее'):
        lemma = splitted[1]

    page = GetPage(lemma)
    soup = BeautifulSoup(page)

    #Get the * table (it includes the paradigm)
    table = soup.find('table',attrs={'cellpadding':'2'})
    try:
        rows = table.find_all('tr')
    except:
        # if no declination table in wiktionary, return false
        return {}

    infldict = {}
    #Singular
    infldict["snom"] = rows[1].find_all('td')[1].contents[0]
    infldict["sgen"] = rows[2].find_all('td')[1].contents[0]
    infldict["sdat"] = rows[3].find_all('td')[1].contents[0]
    infldict["sacc"] = rows[4].find_all('td')[1].contents[0]
    infldict["sinstr"] = rows[5].find_all('td')[1].contents[0]
    infldict["sprep"] = rows[6].find_all('td')[1].contents[0]
    #Plural
    infldict["pnom"] = rows[1].find_all('td')[2].contents[0]
    infldict["pgen"] = rows[2].find_all('td')[2].contents[0]
    infldict["pdat"] = rows[3].find_all('td')[2].contents[0]
    infldict["pacc"] = rows[4].find_all('td')[2].contents[0]
    infldict["pinstr"] = rows[5].find_all('td')[2].contents[0]
    infldict["pprep"] = rows[6].find_all('td')[2].contents[0]

    return infldict


def RusAdjective(lemma):
    """Fetch information about inflection for Russian Nouns"""
    page = GetPage(lemma)
    soup = BeautifulSoup(page)

    #Get the * table (it includes the paradigm)
    table = soup.find('table',attrs={'cellpadding':'2'})
    rows = table.find_all('tr')

    return rows
    infldict = {}
    #Singular masc
    infldict["msnom"] = rows[2].find_all('td')[1].contents[0]
    infldict["msgen"] = rows[3].find_all('td')[1].contents[0]
    infldict["msdat"] = rows[4].find_all('td')[1].contents[0]
    infldict["msacc"] = rows[6].find_all('td')[1].contents[0]
    infldict["msinstr"] = rows[7].find_all('td')[1].contents[0]
    infldict["msprep"] = rows[8].find_all('td')[1].contents[0]
    infldict["mshort"] = rows[9].find_all('td')[1].contents[0]
    #Singular neutr
    infldict["nsnom"] = rows[2].find_all('td')[2].contents[0]
    infldict["nsgen"] = rows[3].find_all('td')[2].contents[0]
    infldict["nsdat"] = rows[4].find_all('td')[2].contents[0]
    infldict["nsacc"] = rows[5].find_all('td')[2].contents[0]
    infldict["nsinstr"] = rows[6].find_all('td')[2].contents[0]
    infldict["nsprep"] = rows[7].find_all('td')[2].contents[0]
    infldict["nshort"] = rows[8].find_all('td')[2].contents[0]
    #Singular fem
    infldict["fsnom"] = rows[2].find_all('td')[3].contents[0]
    infldict["fsgen"] = rows[3].find_all('td')[3].contents[0]
    infldict["fsdat"] = rows[4].find_all('td')[3].contents[0]
    infldict["fsacc"] = rows[5].find_all('td')[3].contents[0]
    infldict["fsinstr"] = rows[6].find_all('td')[3].contents[0]
    infldict["fsprep"] = rows[7].find_all('td')[3].contents[0]
    infldict["fshort"] = rows[8].find_all('td')[3].contents[0]
    #plural
    infldict["pnom"] = rows[1].find_all('td')[4].contents[0]
    infldict["pgen"] = rows[2].find_all('td')[4].contents[0]
    infldict["pdat"] = rows[3].find_all('td')[4].contents[0]
    infldict["pacc"] = rows[5].find_all('td')[4].contents[0]
    infldict["pinstr"] = rows[6].find_all('td')[4].contents[0]
    infldict["pprep"] = rows[7].find_all('td')[4].contents[0]
    infldict["phort"] = rows[8].find_all('td')[4].contents[0]
    return infldict

