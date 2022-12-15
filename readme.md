# Querying Treebanks with Python: The *treesearch* Module

## Introduction

The Python module *treesearch* contains a set of functions designed to query AGDT 2.0 treebanks. Specifically, it is equipped to deal with auxiliaries, where a syntactic relationship may be mediated by a node which is not of interest, and coordinate structures, where syntactically subordinate nodes may be topologically coordinate or superordinate (or vice versa).

The "smart" functions in the module understand how the treebanks work and return the forms that are of interest to the researcher. Additionally, the module is capable of checking whether trees are well-formed and warns the researcher of loops or other annotational errors.


## Initialising the module

Having saved the treesearch.py file in your Python Module Search Path, summon it with

~~~
from treesearch import treesearch

#includes:
#import pandas as pd
#import numpy as np
#import re
~~~

The module accepts csv files and xml files. In both cases, each token minimally to specify a "sentence id", "word id", "relation" and "head", otherwise the code will not work. Thus, for instance, an xml file can be imported as a string:

~~~
xml = open('~sample_trees.xml', 'r', encoding="utf8").read()
~~~

The xml will contain lines formatted as shown below. Word IDs can be numbered sequentially throughout the file, or start again from 1 in each sentence. As long as the word ID and head ID are annotated consistently, the module can deal with this. 

~~~
print(xml[1340:1770])
  <sentence id='1' document_id='' subdoc='1' span=''>
    <word id='1' form='Ἀγαθὰ' lemma='ἀγαθός' postag='a-p---nn-' relation='ExD_CO' ref='' sg='sbs nmn ind ctc' gloss='good' head='2'/>
    <word id='2' form='καὶ' lemma='καί' postag='c--------' relation='COORD' ref='' sg='' gloss='and' head='0'/>
    <word id='3' form='κακά' lemma='κακός' postag='a-p---nn-' relation='ExD_CO' ref='' sg='sbs nmn ind ctc' gloss='bad' head='2'/>
~~~

A csv file, meanwhile, can be imported similarly: 

~~~
df = pd.read_csv("treebank.csv", delimiter=";")
print(csv)
    word id       form relation  head  sentence id
0       100        heu      Aux     0          200
1       101        ego      SBJ   112          200
2       102         in     AuxP   112          200
3       103       domo   ADV_CO   104          200
4       104         et    COORD   102          200
5       105      horto   ADV_CO   104          200
~~~

For the examples in this vademecum, the file in the Github repository can be summoned as:

~~~
df = pd.read_csv("CEIPoM_syntax.csv", delimiter=";")
data = treesearch(df)
data.show()

        Sentence_ID  Token_position  ... Finite_verb Token_ID
161279            1               1  ...       False   161279
161280            1               2  ...       False   161280
165252            2               1  ...        True   165252
165253            2               2  ...        True   165253
165254            2               3  ...        True   165254
            ...             ...  ...         ...      ...
152753         5481               9  ...        True   152753
152754         5481              10  ...        True   152754
152755         5481              11  ...        True   152755
152756         5481              12  ...        True   152756
152757         5481              13  ...        True   152757

[37041 rows x 21 columns]
~~~

Note that this dataframe contains more columns than the obligatory ones noted above. This makes more interesting linguistic queries possible.


### Part 1: General Functionalities

A treesearch object is essentially a pandas DataFrame augmented with some further functions.

~~~
df = pd.read_csv("CEIPoM_syntax.csv", delimiter=";")
data = treesearch(df)
data.show()

data.show()             #prints the DataFrame
data.show(2)            #prints the part of the DataFrame specified by the sentence id (example = Fibula Praenestina)
data.export()           #exports the treesearch object as a pandas DataFrame
data.visualise(5)       #gives a simple visualisation of a tree using indentation (example = Duenos Vase)
~~~

The visualisation function returns something which should look like this, giving you a (simplistic) insight into the structure of the tree:

~~~
data.visualise(5)

0 - 165257 -  - PRED - iovesat
0 - 165257 - 165258 -  - SBJ - deivos
0 - 165257 - 165258 - 165261 -  - ATR - mitat
0 - 165257 - 165258 - 165261 - 165259 -  - SBJ - qoi
0 - 165257 - 165258 - 165261 - 165260 -  - OBJ - med
0 - 165262 -  - AuxC - nei
0 - 165262 - 165267 -  - ADV - sied
0 - 165262 - 165267 - 165265 -  - PNOM - cosmis
0 - 165262 - 165267 - 165265 - 165264 -  - AuxP - endo
0 - 165262 - 165267 - 165265 - 165264 - 165263 -  - ADV - ted
0 - 165262 - 165267 - 165266 -  - SBJ - uirco
~~~

The visualisation function also allows the input and output of a query to be colourised. This is useful when checking an unexpected or outlier result. For instance, suppose smart_daughters(165261) returned [165259, 165260] and we want to check if there is anything wrong with the tree:

~~~c
input = 165261                #input and output can be either integers or lists
output = [165259, 165260]

data.visualise(5, x=input, y=output)

#The below tree will display with additional colour

0 - 165257 -  - PRED - iovesat
0 - 165257 - 165258 -  - SBJ - deivos
0 - 165257 - 165258 - 165261 -  - ATR - mitat <= INPUT
0 - 165257 - 165258 - 165261 - 165259 -  - SBJ - qoi <= OUTPUT
0 - 165257 - 165258 - 165261 - 165260 -  - OBJ - med <= OUTPUT
0 - 165262 -  - AuxC - nei
0 - 165262 - 165267 -  - ADV - sied
0 - 165262 - 165267 - 165265 -  - PNOM - cosmis
0 - 165262 - 165267 - 165265 - 165264 -  - AuxP - endo
0 - 165262 - 165267 - 165265 - 165264 - 165263 -  - ADV - ted
0 - 165262 - 165267 - 165266 -  - SBJ - uirco
~~~

The module revolves around word IDs (or Token_IDs), which are the basis of all syntactic functions. These IDs can be exchanged for various other forms of more human-interpretable information as follows:

~~~
data.form("deivos")          #returns a list of all word ids for which the form is "fefaked" -> [165258]
data.token(165258)           #returns the form for a given word id -> "deivos"
data.tokens([101,102])       #returns the form for a list of word ids -> ['med', 'fefaked']
data.relation(102)           #returns the relation of the specified word id -> "PRED"
data.sentence_id(102)        #returns the sentence id of the specified word id -> 1
data.sentence(102)           #returns a list of all word ids in the same sentence -> [100, 101, 102, 103]
data.pos(102)                #returns the POS tag of the current word id -> ""
data.lemma(102)              #returns the lemma of the current word id -> "facio"
~~~

As the "smart" functions below can be quite slow, it can speed up searches to first filter a list of relevant tokens based on morphological or formal criteria. For example, suppose we are interested only in the syntactic function of forms of *facio*, we can use:

~~~
data.subset("lemma","video1")            #returns a list of ids where lemma = "video1" -> [155, 162]
data.subset("form","fefaked")            #returns a list of ids where form = "fefaked" -> [102]
~~~

If we wish to use more precise POS searches, the regex equivalent of this function should be used. So to filter accusative nouns:

~~~
data.regex_subset("pos","n......a.")            #returns a list of ids where the POS indicates an accusative noun -> [142, 152]
~~~

Use the intersection of lists to filter by multiple criteria

~~~
l1 = data.subset("form","consilia")                  #returns ids where form = "consilia"
l2 = data.regex_subset("pos",".......a.")            #returns ids where case = accusative
l3 = data.regex_subset("pos","n........")            #returns ids where part of speech = noun

l = list(set(l1) & set(l2) & set(l3))
~~~



### Part 2: Topological "Dumb" Functions

A first set of syntactic functions are described here as "topological" (or "dumb") functions, which just perform searches based on the tree topology and do not understand that syntactic relationships are not always hierarchical.

The basic underlying functions are the following:

~~~
data.direct_tree_parent(100)            #returns the direct topological parent as an integer -> 102
data.tree_parents(100)                  #returns a list of topological parents in order to the root -> [102, 0]
data.direct_tree_children(102)          #returns a list of direct topological children -> [100, 101, 103]
data.tree_children(102)                 #returns a list of all topological children (regardless of how many nodes removed) -> [100, 101, 103]
~~~

For queries where coordination and Aux relations are irrelevant, or datasets large enough that such cases can be ignored, these functions may be sufficient for more purposes (and much faster than the "smart" functions).


### Part 3: Syntactic "Smart" Functions

A second set of syntactic functions understands coordination and aux relations, and finds the tokens a researcher is likely to be primarily interested in.

~~~
data.smart_parents(100)                 #returns the true syntactic parent(s) of the current word id -> [102]
data.smart_daughters(102)               #returns the true syntactic daughter(s) of the current word id -> [100, 101, 103]
data.smart_siblings(100)                #returns fellow coordinands of the current word id (if any) -> [100]
~~~

Let's find a tree with some COORD and Aux, to illustrate the power of these functions.

~~~
lat = data.regex_subset("Language","Latin")       #let's limit to Latin for illustrative purposes
cos = data.regex_subset("Relation","_CO")       #find some Token_IDs with "_CO"
aux = data.regex_subset("Relation","Aux")       #find some Token_IDs with "Aux"

s1 = [data.sentence_id(i) for i in cos]              #get the intersection of their Sentence_IDs (we're not just interested in individual words)
s2 = [data.sentence_id(i) for i in aux]
s3 = [data.sentence_id(i) for i in lat]

s = list(set(s1) & set(s2) & set(s3))

len(s)
97
~~~

We can then "browse" through the 97 results using the visualisation function, until we find an interesting tree:

~~~
data.visualise(s[0])
data.visualise(s[1])
data.visualise(s[2])
~~~

For illustrative purposes, notice the inscription shown below:

~~~
data.visualise(s[6])

0 - 418503 -  -  - [[e]]
0 - 502035 -  - COORD - que
0 - 502035 - 418501 -  - AuxP - apur
0 - 502035 - 418501 - 418502 -  - ADV - finem
0 - 502035 - 418501 - 418502 - 418504 -  - ATR - calicom(!)
0 - 502035 - 418505 -  - AuxP - en
0 - 502035 - 418505 - 418506 -  - ADV - urb/id
0 - 502035 - 418505 - 418506 - 418507 -  - ATR - casontoni/a
0 - 502035 - 418510 -  - PRED_CO - atolero
0 - 502035 - 418510 - 418508 -  - SBJ - socie
0 - 502035 - 418510 - 418509 -  - ADV - dono/m
0 - 502035 - 418510 - 418511 -  - OBJ - actia
0 - 502035 - 418510 - 418512 -  - AuxP - pro
0 - 502035 - 418510 - 418512 - 418513 -  - ADV - l[ecio]nibus
0 - 502035 - 418510 - 418512 - 418513 - 418514 -  - ATR - mar/tses
0 - 502035 - 515240 -  - PRED_CO - -
0 - 502035 - 515240 - 418497 -  - SBJ - caso
0 - 502035 - 515240 - 418497 - 418498 -  - ATR - cantovio/s
0 - 502035 - 515240 - 418497 - 418499 -  - ATR - aprufclano
0 - 502035 - 515240 - 418500 -  - OBJ - cei/p()
~~~

Translation: At the Esalican bonudary in the city Casontonia, Caso Cantovios Aprufclanos set up pillars and his allies brought a sacred gift to Angitia on behalf of Marsian legions.

Imagine that we want to find the parent of *finem* "boundary" (Token_ID 418502). Using the "dumb" function, this finds:

~~~
t = data.direct_tree_parent(418502)
t = data.token(t)

apur
~~~

The preposition "apur", for some purposes, might be the right answer. However, for other purposes the syntactic head is likely to be the two coordinated predicates which this adverbial qualifies (Caso ??? and the allies brought ... at the Esalican boundary). The smart function ignores Aux and COORD and finds them, even though they are not syntactically superordinate:

~~~
t = data.smart_parents(418502)
t = data.tokens(t)

['atolero', '-']
~~~

Conversely, if we have the Token_ID of *atolero*, but we want to find the Token_ID of its (illegible) sister, we simply use:

~~~
t = data.smart_siblings(418510)
t = data.tokens(t)

['atolero', '-']
~~~

We get the same answer: the function understands that other topological coordinates, such as AuxP *apur*, are not its sisters. This function even returns the right answer with multiple layers of coordination embedded within each other.

Finally, suppose we want to get the children of *atolero*, which means its own specific arguments and satellites, but also those it shares with its sibling (but not those belonging exclusively to its sibling). This gives:

~~~
t = data.smart_children(418510)
t = data.tokens(t)

['finem', 'urb/id', 'socie', 'dono/m', 'actia', 'l[ecio]nibus']
~~~

Which is correct, and which a researcher will probably find more informative than a string of Auxes.


## Some More Complex Examples

This is a step-by-step example of a complex linguistic query using the various functionalities of this module:

> Are nominal accusative objects more likely to be preposed or postposed depending on whether or not they are in a main sentence, and does the answer vary from language to language?

First, import the CEIPoM database:

~~~
from treesearch import treesearch

df = pd.read_csv("~CEIPoM_syntax.csv", delimiter=";")
data = treesearch(df)
data.show()
~~~

We could perform the syntactic part of the query first, and then filter out accusative nominals. However, the smart functions are slow, so this would be a huge waste of time. Instead, we filter the fast stuff first:

~~~
l1 = data.regex_subset("POS",".......a.")               # only accusatives are of interest
l2 = data.regex_subset("Relation","OBJ")                # only objects are of interest, note that regex will also get OBJ_CO

l = list(set(l1) & set(l2))

len(l)
1108
~~~

As this is a lot of results, it's a good idea to test the query on a subset first:

~~~
#l = l[:10]

result = []
check = []

for i in l:
    s = data.smart_siblings(i)                                  #get all fellow coordinands
    
    if sorted(s) in check:
        continue                                                #if we've already had one of its coordinands, skip this iteration
    check.append(sorted(s))                                     #remember its coordinands so that we don't do it twice
    
    s_pos = [data.information("Token_position",i) for i in s]   #get the position of coordinands (this is for word order: Token_ID is arbitrary in CEIPoM)
    
    p = data.smart_parents(i)                                   #get all parents
    p_pos = [data.information("Token_position",i) for i in p]   #get the position of parents
    
    rel = data.relation(p)                                      #get the relation of parents (this function can handle lists)
    
    if max(s) < min(p):                                         #check if all coordinands precede all parents
        order = True
    elif max(p) < min(s):                                       #check if all parents precede all coordinands
        order = False
    else:                                                       #ignore weird cases where coordinands are intertwined
        order = None

    #print(l.index(i),l)                                        #optional, to keep track of progress during long operations
    result.append((rel, order))
~~~

This gives a list of tuples, as follows:

~~~
[('PRED', True),
 ('PRED', True),
 ('PRED', True),
 ('PRED', False),
 ('PRED', True),
 ('PRED', False),
 ('PRED', False),
 ('ATR', False),
 ('PRED', True),
 ('ADV', True)]
~~~

Now we can calcate












However, objects may be coordinated (thus OBJ_CO), and we don't want to count them twice. Moreover, if they're linked to their head via an Aux, or if their head is coordinated, or if their head isn't topologically superordinate, we don't want to miss them.

This is where the *treesearch* module becomes useful. We formulate the same query, but with a smart function:

~~~
l = data.regex_subset("relation","OBJ.*")         #so that we don't filter out OBJ_CO

result = []
check = []

for i in l:
    s = data.smart_siblings(i)                    #get all fellow coordinands
    if sorted(s) in check:
        continue                                  #if we've already had one of its coordinands, skip this iteration
    check.append(sorted(s))
    p = data.smart_parents(i)                     #get all parents
    
    if max(s) < min(p):                           #check if all coordinands precede all parents
        result.append(True)
    elif max(p) < min(s):                         #check if all parents precede all coordinands
        result.append(False)
    else:                                         #some objects precede while others follow, and similar cases
        result.append(None)

l.count(True)
l_count(False)
~~~

**Are objects more likely to be preposed or postposed depending on whether they are in a main clause or not?**






