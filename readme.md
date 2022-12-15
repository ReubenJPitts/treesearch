## Python Functions for Syntax

### Introduction

This Python module contains a set of functions designed to query AGDT 2.0 treebanks. Specifically, it is equipped to deal with auxiliaries, where a syntactic relationship may be mediated by a node which is not of interest, and coordinate structures, where syntactically subordinate nodes may be topologically coordinate or superordinate (or vice versa). The "smart" functions in the module understand how the treebanks work and return the forms that are of interest to the researcher. Additionally, the module is capable of checking whether trees are well-formed and warns the researcher of loops or other annotational errors.

### Input and output

The module takes a csv file, an xml file or a pandas dataframe as its input. Minimally, these files should have a column named "Token_ID", "Head" and "Relation", where Token_ID and Head are integers, describing respectively a unique identifier of a token and that of its syntactic head, and Relation, specifying its syntactic relationship with its head.


The xml, typically with the following structure:


## Using the module: some simple examples

First save the module in your Python Module Search Path (PMSP)
    
    
    


An xml can be imported as follows:

~~~
df = open('aesop.xml', 'r', encoding="utf8").read()
data = treesearch(df)
data.show()
~~~

This will display a dataframe
