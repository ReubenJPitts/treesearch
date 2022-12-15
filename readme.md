## Quering Treebanks with Python: The *treesearch* module

### Introduction

The Python module *treesearch* contains a set of functions designed to query AGDT 2.0 treebanks. Specifically, it is equipped to deal with auxiliaries, where a syntactic relationship may be mediated by a node which is not of interest, and coordinate structures, where syntactically subordinate nodes may be topologically coordinate or superordinate (or vice versa).

The "smart" functions in the module understand how the treebanks work and return the forms that are of interest to the researcher. Additionally, the module is capable of checking whether trees are well-formed and warns the researcher of loops or other annotational errors.


### Initialising the module

Having saved the treesearch.py file in your Python Module Search Path, summon it with

~~~
from treesearch import treesearch
~~~

The module accepts csv files and xml files. In both cases, each token minimally to specify a "sentence id", "word id", "relation" and "head", otherwise the code will not work. Thus, for instance, an xml file can be imported as a string:

~~~
xml = open('~aesop.xml', 'r', encoding="utf8").read()
~~~

The xml will contain lines formatted as follows. Word IDs can be numbered sequentially throughout the file, or start again from 1 in each sentence. As long as the word ID and head ID are annotated consistently, the module can deal with this. 

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


## Using the module: some simple examples

A simple test xml is provided in.

~~~
from treesearch import treesearch
df = open('~aesop.xml', 'r', encoding="utf8").read()
~~~

data = treesearch(df)
data.show()
~~~

This will display a dataframe
