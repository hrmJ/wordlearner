from bs4 import BeautifulSoup
import urllib


def GetPage(wordstring = 'лазить'):
    """Get wiktionary page object for parsing"""
    word = urllib.request.quote(wordstring.encode('utf-8'))
    address = "http://ru.wiktionary.org/wiki/" + word
    try:
        wikipage = urllib.request.urlopen(address)
        wphtml = wikipage.read()
        wikipage.close()
        return wphtml
    except urllib.error.HTTPError:
        print('Cannot fetch information for the word {}'.format(wordstring))
        input('Press enter to continue.')
        return False

def FetchInflectionData(word):
    """Fetch information about inflection for Russian verbs"""

    print('Inflecting {}...'.format(word.lemma))
    #Check for A+ N
    splitted = word.lemma.split()
    if word.pos=='N' and len(splitted)>1 and  splitted[0][-2:] in ('ый','ой','ая','ое','ий','яя','ее'):
        page = GetPage(splitted[1])
    else:
        page = GetPage(word.lemma)

    ##################################################################################
    if not page:
        #if an error occured during fetching the url
        return False
    try:
        soup = BeautifulSoup(page)
    except TypeError:
        input('Problem reading data for {} (type error)'.format(word.lemma))
        return False

    #Get the * table (it includes the paradigm)
    table = soup.find('table',attrs={'cellpadding':'2'})
    if table is None:
        return False
    rows = table.find_all('tr')

    ##################################################################################
    infldict = {}

    #Verbs:
    if word.pos == 'V':
        #present tense
        categories = {"s1pres":(1,1), "s2pres":(2,1), "s3pres":(3,1), "p1pres":(4,1), "p2pres":(5,1), "p3pres":(6,1)}
        #past tense + imperative mode
        categories.update({"spastmasc":(3,2),"spastfem":(3,2),"ppast":(4,2),"simp":(2,3)})

    #Nouns:
    elif word.pos == 'N':
        #Singular
        categories = {"snom": (1,1), "sgen":(2,1), "sdat":(3,1), "sacc":(4,1), "sinstr":(5,1), "sprep":(6,1)}
        #Plural
        categories.update({"pnom": (1,2), "pgen":(2,2), "pdat":(3,2), "pacc":(4,2), "pinstr":(5,2), "pprep":(6,2)})

    #Adjectives:
    elif word.pos == 'A':
        #Singular masc
        categories = {"msnom":(2,1), "msgen":(3,1), "msdat":(4,1), "msacc":(6,1), "msinstr":(7,1), "msprep" :(8,1), "mshort" :(9,1)}
        #Singular neutr
        categories.update({"nsnom":(2,2), "nsgen":(3,2), "nsdat":(4,2), "nsacc":(5,3), "nsinstr":(7,2), "nsprep" :(8,2), "nshort" :(9,2)})
        #Singular fem
        categories.update({"fsnom":(2,3), "fsgen":(3,3), "fsdat":(4,3), "fsacc":(5,4), "fsinstr":(7,3), "fsprep" :(8,3), "fshort" :(9,3)})
        #plural
        categories.update({"pnom":(2,4), "pgen":(3,4), "pdat":(4,4), "pacc":(6,2), "pinstr":(7,4), "pprep" :(8,4), "pshort" :(9,4)})

    return Inflectiondict(rows,categories)

class Inflectiondict(dict):
    """Special dictionaries to contain information about inflection
    Initialized on base of wiktionary conjugation/declination table
    """

    def __init__(self, rows, categories):
        """ 
        In the coordinates dict, the values are tuples
        orederd as (row,column)"""
        for category, coordinates in categories.items():
            #Fetch the information from the right row and column according to the coordinates
            if category == 'spastfem':
                #special case: verb: past fem
                self[category] = rows[coordinates[0]].find_all('td')[coordinates[1]].contents[2].strip()
            else:
                try:
                    self[category] = rows[coordinates[0]].find_all('td')[coordinates[1]].contents[0]
                    if category == 'fsinstr':
                        #special case: adjective/fem/instr
                        splitted = self[category].split()
                        self[category] = splitted[0]
                except IndexError:
                    print('Category {} missing, skipping it.'.format(category))

