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

