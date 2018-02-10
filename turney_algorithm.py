import os
import math
import nltk
import re

def read_document(filename):
    file = open(filename,"r",encoding="utf8").read()
    return file

def make_datasets(data_path, numfolds = 10):
    klasses = os.listdir(data_path)
    datasets = []
    filenames = {klass: sorted(os.listdir(data_path + klass + '/')) for klass in klasses}
    for fold in range(numfolds):
        trains = {klass: [] for klass in klasses}
        tests = {klass: [] for klass in klasses}
        for klass in klasses:
            for filename in filenames[klass]:
                if filename[2] == str(fold):
                    tests[klass].append(data_path + klass + '/' + filename)
                    trains[klass].append(data_path + klass + '/' + filename)
                else:
                    trains[klass].append(data_path + klass + '/' + filename)
        datasets.append({'train': trains, 'test': tests})
    return datasets

def find_pattern(postag):
    tag_pattern = []
    for k in range(len(postag)-2):
        if( postag[k][1]=="JJ" and (postag[k+1][1]=="NN" or postag[k+1][1]=="NNS")) :
            tag_pattern.append("".join(postag[k][0])+" "+"".join(postag[k+1][0]))
            
        elif( (postag[k][1]=="RB" or postag[k][1]=="RBR" or postag[k][1]=="RBS") and postag[k+1][1]=="JJ" and postag[k+2][1]!="NN" and postag[k+2][1]!="NNS"):
            tag_pattern.append("".join(postag[k][0])+" "+"".join(postag[k+1][0]))
            
        elif( postag[k][1]=="JJ" and postag[k+1][1]=="JJ" and postag[k+2][1]!="NN" and postag[k+2][1]!="NNS"):
            tag_pattern.append("".join(postag[k][0])+" "+"".join(postag[k+1][0]))
    
        elif( (postag[k][1]=="NN" or postag[k][1]=="NNS") and postag[k+1][1]=="JJ" and postag[k+2][1]!="NN" and postag[k+2][1]!="NNS"):
            tag_pattern.append("".join(postag[k][0])+" "+"".join(postag[k+1][0]))
    
        elif( (postag[k][1]=="RB" or postag[k][1]=="RBR" or postag[k][1]=="RBS") and (postag[k+1][1]=="VB" or postag[k+1][1]=="VBD" or postag[k+1][1]=="VBN" or postag[k+1][1]=="VBG")):
            tag_pattern.append("".join(postag[k][0])+" "+"".join(postag[k+1][0]))
    return tag_pattern

def near_operator(phrase, word, text):
    try:
        string= word+r'\W+(?:\w+\W+){0,500}?'+phrase+r'|'+phrase+r'\W+(?:\w+\W+){500}?'+word
        freq_phrase_near_word=(len(re.findall(string,text)))
        return freq_phrase_near_word
    except:
        return 0


class Turney(object):

    def __init__(self, datasets):
        self.datasets = datasets
        self.pos_prases_hits = []
        self.neg_phrases_hits = []
        self.pos_hits = 0.01
        self.neg_hits = 0.01
        self.accuracy = 0
        
    def turney(self):
        for boolean, test_klass in enumerate(['pos', 'neg']):
            for i, data in enumerate(self.datasets[0]['test'][test_klass]):
                phrases = []
                text = read_document(data)
                phrases = find_pattern(nltk.pos_tag(nltk.word_tokenize(text)))
                self.pos_phrases_hits = [0.01]* len(phrases)
                self.neg_phrases_hits = [0.01]* len(phrases)
                self.pos_hits = 0.01
                self.neg_hits = 0.01
                
                for train_klass in ['pos', 'neg']:
                    for file in self.datasets[0]['train'][train_klass]:
                        txt_file = read_document(file)
                        for ind, phrase in enumerate(phrases):
                            self.pos_phrases_hits[ind] += near_operator(phrase, "great", txt_file)
                            self.neg_phrases_hits[ind] += near_operator(phrase, "poor", txt_file)
                            self.pos_hits += txt_file.count("great")
                            self.neg_hits += txt_file.count("poor")
                                
                self.calculate_sentiment(boolean)
        print("Accuracy: ", ((self.accuracy/200)*100))
            
    def calculate_sentiment(self, is_negative = 0):
        polarities = [0] * len(self.pos_phrases_hits)
        for i in range(len(self.pos_phrases_hits)):
            polarities[i] = math.log((self.pos_phrases_hits[i] * self.neg_hits) / (self.neg_phrases_hits[i] * self.pos_hits),2)
        pmi = sum(polarities)/len(polarities)
        if ((pmi > 0 and is_negative == 0) or (pmi < 0 and is_negative == 1)):
            self.accuracy += 1
            
def main():
    DATA_PATH = './imdb1/'
    datasets = make_datasets(DATA_PATH)
    turney = Turney(datasets)
    turney.turney()
              
if __name__ == "__main__":
    main()
    
    