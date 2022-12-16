
#########################################
#### Querying Treebanks with Python #####
#########################################

import pandas as pd
import re

def collapse(l):
    return(list(dict.fromkeys([i for j in l for i in j])))
    #collapses lists of lists and removes any resulting duplicates

def adapt_csv(df):
    df.columns = df.columns.str.replace(r"word id", "Token_ID")
    df.columns = df.columns.str.replace(r"sentence id", "Sentence_ID")
    df.columns = df.columns.str.replace(r"relation", "Relation")
    df.columns = df.columns.str.replace(r"head", "Head")
    df.columns = df.columns.str.replace(r"lemma", "Lemma")
    df.columns = df.columns.str.replace(r"form", "Form")
    df.columns = df.columns.str.replace(r"POS_code", "POS")
    df['Sentence_ID'] = df['Sentence_ID'].fillna(0).astype(int)
    df['Token_ID'] = df['Token_ID'].fillna(0).astype(int)
    df['Head'] = df['Head'].fillna(0).astype(int)
    df = df.fillna("")
    return df
    #adds some resilience to csvs with slightly different titles
    
def xml_to_df(xml):    
    xml = xml.split('\n')
    xml = [i.strip() for i in xml]
    queries = ["sentence id='.*?'","word id='.*?'","head='.*?'","relation='.*?'","lemma='.*?'","form='.*?'","postag='.*?'"]
    sid = False
    data = []
    for line in xml:
        record = []
        for i, query in enumerate(queries):
            results = re.findall(query,line)
            try:
                new = results[0]
                new = new[len(query)-4:-1]
                if query == "sentence id='.*?'":
                    sid = new
            except IndexError:
                if query == "sentence id='.*?'":
                    new = sid
                else:
                    new = ""
            record.append(new)
        data.append(record)
    data = pd.DataFrame(data,columns=["Sentence_ID","Token_ID","Head","Relation","Lemma","Token","POS"])
    data = data[data["Token_ID"] != ""]
    return data
    #turns AGDT-style xmls into dataframes

def unique_token_ids(df):
    n = 100
    df["New"] = list(range(n, n + len(df)))
    df = df.merge(df, how="left", right_on=["Sentence_ID", "Token_ID"], left_on=["Sentence_ID", "Head"], suffixes=("","_y"))
    df['New_y'] = df['New_y'].fillna(0).astype(int)
    df = df[["Sentence_ID","New","New_y","Relation","Lemma","Token","POS"]]
    df = df.rename(columns={'New': 'Token_ID', 'New_y': 'Head'})
    df['Sentence_ID'] = df['Sentence_ID'].astype(int)
    df['Token_ID'] = df['Token_ID'].astype(int)
    return df
    #modifies dataframes where token_id count starts from 1 in each sentence
    
class TreeSearch:
    
    ### 0 ### INITIALISE A DATAFRAME
    def __init__(self, data):
        if isinstance(data, pd.DataFrame):
            self.df = adapt_csv(data)
        if isinstance(data, str):
            self.df = xml_to_df(data)
        if len(list(dict.fromkeys(list(self.df["Token_ID"])))) < len(list(self.df["Token_ID"])):
            self.df = unique_token_ids(self.df)
        self.df = self.df.set_index(["Token_ID"])
        self.df.index.name = None
        self.df["Token_ID"] = self.df.index
        #creates a dataframe object
        
    def show(self,s="x"):
        if s == "x":
            print(self.df)
        else:
            print(self.df[self.df["Sentence_ID"] == s])
        #show the whole dataframe, or a chosen sentence
        
    def export(self,s="x"):
        if s == "x":
            return self.df
        else:
            return self.df[self.df["Sentence_ID"] == s]
        #export the dataframe object, or a chosen sentence
                
             
    ### 1 ### GENERAL FUNCTIONS
    def form(self, f):
        return list(self.df[self.df["Token"] == f].index)
        #returns a list of token_ids for a form
        
    def relation(self, i):
        if isinstance(i, list):
            try:
                i = i[0]
            except:
                return ""
        try:
            return self.df.loc[[i]]["Relation"].item()
        except:
            return ""
        #returns the relation of the current token
        #tries to return the relation of the first token of lists (can be convenient)

    def pos(self, i):
        try:
            return self.df.loc[[i]]["POS"].item()
        except:
            return ""    
        #returns a POS-tag
        
    def lemma(self, i):
        try:
            return self.df.loc[[i]]["Lemma"].item()
        except:
            return ""    
        #returns a Lemma
        
    def token(self, i):    
        try:
            return self.df.loc[[i]]["Token"].item()
        except:
            return ""
        #returns a token
    
    def tokens(self, l):    
        output = []
        for i in l:
            try:
                output.append(self.df.loc[[i]]["Token"].item())
            except:
                output.append("")
        return output
        #returns a list of tokens
        
    def show_ids(self, l):
        print(self.df[self.df.index.isin(l)])
        #shows subset of dataframe
        
    def sentence_id(self, i):
        return int(self.df.loc[[i]]["Sentence_ID"])
        #returns the sentence_id of the current token

    def sentence(self, i):
        return list(self.df[self.df["Sentence_ID"] == self.sentence_id(i)].index)
        #returns all token_ids in the same sentence as the current token
    
    def check_relation(self, r, l):
        return [i for i in l if self.relation(i) == r]
        #filters all tokens from a list l with relation r

    def treetop(self, i):
        subset_df = self.df[self.df["Sentence_ID"] == self.sentence_id(i)]
        return list(subset_df[subset_df["Head"] == 0].index)
        #returns the "top" of the sentence of the current token, that is, the tokens
        # which are immediately subordinate to the root(0)

    def subset(self, column, i):
        return list(self.df[self.df[column] == i].index)
        #a more general function for filtering a dataframe based on a column

    def regex_subset(self, column, i):
        return list(self.df[self.df[column].str.contains(i, regex=True)].index)
        #a more general function for filtering a dataframe based on a column, using regex
        
    def information(self, column, i):
        try:
            return self.df.loc[[i]][column].item()
        except:
            return ""
        #a flexible function for retrieving any piece of information for a single token


    ### 2 ### TOPOLOGICAL "DUMB" FUNCTIONS
    def direct_tree_parent(self, i):
        try:
            return int(self.df.loc[[i]]["Head"])
        except:
            return 0
        #returns the direct topological parent of the current token as an integer

    def tree_parents(self, i):
        l = []
        while i != 0:
            i = self.direct_tree_parent(i)
            l.append(i)
        return l
        #returns a consecutive list of topological parents to the root of the tree

    def same_tree_parents(self, i):
        r = self.relation(i)
        l = []
        for p in self.tree_parents(i):
            if p != 0 and self.relation(p) == r:
                l.append(p)
            else:
                break
        return l
        #returns a consecutive list of topological parents as long as they have
        # the same relation as the current token (important for some subsequent
        # functions)

    def direct_tree_children(self, i):
        return list(self.df[self.df["Head"] == i].index)
        #returns all direct topological children of the current token

    def tree_children(self, i):
        l = self.direct_tree_children(i)
        while True:
            check = l
            l = [l] + [self.direct_tree_children(i) for i in l]
            l = collapse(l)
            if l == check:
                break
        return l
        #returns all topological children of the current token

    def same_tree_children(self, i):
        r = self.relation(i)
        l = []
        l = self.check_relation(r,self.direct_tree_children(i))
        while True:
            check = l
            l = [l] + [self.check_relation(r,self.direct_tree_children(i)) for i in l]
            l = collapse(l)
            if l == check:
                break
        return l
        #returns contiguous topological children with the same relation

    def tree_siblings(self, i):
        i = self.direct_tree_parent(self, i)
        if i == 0:
            return self.treetop(i)
        else:
            return self.tree_children(i)
        
    def direct_aux_parent(self, i):
        i = self.direct_tree_parent(i)
        if "Aux" in self.relation(i):
            i = self.direct_tree_parent(i)
        return i
        #returns topological parent in a manner blind to Auxes: that is, returns
        # topological parent but skips any Aux tokens

    def direct_aux_children(self, i):
        l = self.direct_tree_children(i)
        m = [self.direct_tree_children(i) for i in l if "Aux" in self.relation(i)]
        l = [i for i in l if "Aux" not in self.relation(i)]
        return collapse([l] + m)
        #returns immediate topological children but skipping Aux

    def visualise(self, s, x=None, y=None):
        if isinstance(y, int):
            y = [y]
        if isinstance(x, int):
            x = [x]
        l = list(self.df[self.df["Sentence_ID"] == s].index)    
        pedigree = []
        for i in l:
            p = [str(self.token(i)), str(self.relation(i)), "$", str(i)] + [str(i) for i in self.tree_parents(i)]
            p = list(reversed(p))
            p = "\033[0;37m" + " - ".join(p)
            if isinstance(y, list) and i in y:
                p = p.replace("$","\033[0;35m")
                p = p + "\033[0;35m <= OUTPUT"
            else:
                p = p.replace("$","\033[0;38m")
            if isinstance(x, list) and i in x:
                p = p + "\033[0;33m <= INPUT"
            pedigree.append(p)
        pedigree = sorted(pedigree)
        for p in pedigree:
            print(p)
        #uses the "dumb" functions to visualise a tree, colourised if desired
        
    
    ### 3 ### COORDINATION FUNCTIONS
    def check_if_co(self, i, r):
        if self.relation(i) == r:
            return True
        elif "Aux" in self.relation(i) and len([i for i in self.direct_tree_children(i) if self.relation(i) == r]) > 0:
            return True
        else:
            return False
        #checks if a token either is a relevant instance of a relation + _CO, or
        # governs such a relation as an Aux. So entering "OBJ_CO" as r checks both
        # if the token is an OBJ_CO, but also if it is, say, an AuxP governing an
        # OBJ_CO. Important for subsequent functions.

    def check_coord(self, i):
        l = self.direct_aux_children(i)
        try:
            return self.relation([i for i in l if "_CO" in self.relation(i)][0])
        except:
            return ""
        #returns, as a string, the relation that a coordinator is coordinating,
        # and gives empty string if it doesn't find anything relevant

    def get_coord(self, i):
        if self.relation(i) != "COORD":
            return ""
        r = self.check_coord(i)
        l = self.same_tree_children(i) + self.same_tree_parents(i) + [i]
        return [i for i in l if self.check_coord(i) == r or self.check_coord(i) == "" or r == ""]
        #gets subordinate or superordinate coordinators for the same relation; if
        # it's not sure whether a coordinator is related it will give the benefit 
        # of the doubt

    def get_coord_up(self, i):
        if self.relation(i) != "COORD":
            return ""
        r = self.check_coord(i)
        l = self.same_tree_parents(i) + [i]
        return [i for i in l if self.check_coord(i) == r or self.check_coord(i) == "" or r == ""]
        #same as above but only searches upwards

    def get_coord_down(self, i):
        if self.relation(i) != "COORD":
            return ""
        r = self.check_coord(i)
        l = self.same_tree_children(i) + [i]
        return [i for i in l if self.check_coord(i) == r or self.check_coord(i) == "" or r == ""]
        #same as above but only searches downwards

    def direct_co_children(self, i):
        c = self.get_coord_down(i)
        r = self.check_coord(i)
        l = collapse([self.direct_tree_children(i) for i in c])
        return [i for i in l if self.check_if_co(i,r) == True]
        #finds tokens which are coordinated by a COORD, including subordinate
        # coordinators, where relevant fetching the token_id of their aux instead;
        # returns empty list if it can't interpret the token as a coord

    def direct_aux_co_children(self, i):
        c = self.get_coord_down(i)
        r = self.check_coord(i)
        l = collapse([self.direct_aux_children(i) for i in c])
        return [i for i in l if self.relation(i) == r]
        #ditto but ignores the aux and instead gets the token_id of the coordinand

    def direct_nonco_children(self, i):
        c = self.get_coord_up(i)
        r = self.check_coord(i)
        l = collapse([self.direct_tree_children(i) for i in c])
        l = [i for i in l if self.check_if_co(i,r) == False]
        return [i for i in l if self.relation(i) != "COORD" or self.check_coord(i) != r]
        #returns topological children of a coord which it does not coordinate,
        # and which are thus syntactically subordinate to its coordinands, including
        # those of topologically superordinate coordinators; if it can't interpret
        # a token as a coord just gets regular direct topological children
    
    def direct_aux_nonco_children(self, i):
        c = self.get_coord_up(i)
        r = self.check_coord(i)
        l = collapse([self.direct_aux_children(i) for i in c])
        l = [i for i in l if self.relation(i) != r]
        return [i for i in l if self.relation(i) != "COORD" or self.check_coord(i) != r]
        #ditto but ignores auxes


    ### 4 ### SYNTACTIC "SMART" FUNCTIONS
    def smart_parents(self, i):
        p = i
        while True:
            p = self.direct_tree_parent(p)
            if p == 0:
                return [0]
            if self.relation(p) == "COORD" and self.check_if_co(i,self.check_coord(p)) == False:
                return self.direct_aux_co_children(p)
            if self.relation(p) == "COORD" and self.check_if_co(i,self.check_coord(p)) == True:
                continue
            elif "Aux" in self.relation(p):
                continue
            else:
                break
        return [p]
        #gets the syntactic parents you really want, ignoring COORD and Aux whilst
        # understanding what they mean syntactically
        
    def smart_children(self, i):
        if "Aux" in self.relation(i):
            child = self.direct_tree_children(i)
            if len(child) > 0 and self.relation(child[0]) == "COORD":
                return self.direct_aux_co_children(child[0])
            else:
                return child
        elif self.relation(i) == "COORD":
            return self.direct_aux_co_children(i)
        else:
            l = [j for j in self.sentence(i) if i in self.smart_parents(j)]
            return [i for i in l if self.relation(i) != "COORD" and "Aux" not in self.relation(i)]
        #gets the syntactic children you really want, ignoring COORD and Aux whilst
        # understanding what they mean syntactically

    def smart_siblings(self, i):
        if "_CO" in self.relation(i):
            p = self.direct_aux_parent(i)
            c = self.get_coord(p)
            r = self.check_coord(p)
            l = collapse([self.direct_aux_children(i) for i in c])
            return [i for i in l if self.relation(i) == r]
        else:
            return [i]
        #gets all coordinated siblings of i, including of sub- or superordinate
        # coordinators (simply returns [i] if there are none)


    ### 5 ### DIAGNOSING DISEASED TREES
    def check_tree_root(self, s):
        if 0 in list(self.df[self.df["Sentence_ID"] == s]["Head"]) == False:
            print("This tree appears to lack a root")
            return False
        else:
            return True
        #function checks if tree is rooted; note that all functions should be
        # resilient to unrooted branches
        
    def check_tree_complete_heads(self, s):
        if all(isinstance(item, int) for item in list(self.df[self.df["Sentence_ID"] == s]["Head"])):
            return True
        else:
            print("Not all tokens in this tree have valid heads")
            return False
        #checks if tree contains all requisite heads; can be ignored
        
    def check_tree_complete_relations(self, s):
        if all(isinstance(item, str) for item in list(self.df[self.df["Sentence_ID"] == s]["Relation"])):
            return True
        else:
            print("Not all tokens in this tree have valid relations")
            return False
        #checks if tree contains all requisite relations; can be ignored
        
    def check_tree_loops(self, s):
        l = list(self.df[self.df["Sentence_ID"] == s].index)
        for i in l:
            loop = []
            while i != 0:
                loop.append(i)
                i = self.direct_tree_parent(i)
                if len(list(dict.fromkeys(loop))) < len(loop):
                    print("This tree appears to contain a loop")
                    return False
        return True
        #checks if tree contains loops; can be ignored, but best to tweak code with
        # a loop breaker, otherwise it will repeat infinitely

    def check_tree_aux_children(self, s):
        l = list(self.df[self.df["Sentence_ID"] == s].index)
        l = [i for i in l if "Aux" in self.relation(i)]
        for i in l:
            if len(self.direct_tree_children(i)) > 1:
                print("This tree appears to contain Auxes with multiple children")
                return False               
            if any("Aux" in self.relation(j) for j in self.direct_tree_children(i)):
                    print("This tree appears to contain consecutive Auxes")
                    return False                 
        return True
        #checks if auxes are isolated linkers as they should be; best not to ignore
        # except for basic topological queries
    
    def check_tree_aux_co(self, s):
        l = list(self.df[self.df["Sentence_ID"] == s].index)
        l = [self.relation(i) for i in l]
        for i in l:
            if ("Aux" in i) + ("_CO" in i) + ("COORD" in i) > 1:
                print("This tree appears to contain malformed relation strings")
                return False
        return True
        #checks for strings that combine diagnostic substrings such as Aux or _CO;
        # probably best not to ignore except for basic topological queries
        
    def check_tree_coord(self, s):
        l = list(self.df[self.df["Sentence_ID"] == s].index)
        l = [i for i in l if "COORD" in self.relation(i)]
        for i in l:
            if self.check_coord(i) == "":
                print("This tree doesn't appear to have coordinands for all coordinators")
                return False
        return True
        #checks if all coordinators are specified; can be ignored but might misbehave
        # with queries that are sensitive to coordination phenomena
      