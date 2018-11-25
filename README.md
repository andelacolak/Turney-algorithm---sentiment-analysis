# Turney-algorithm wih internal search
<p>Turney's algorithm with adaptation for the internal search of phrases near some word. Reason for this kind of adaptation is that infinite number of search engine API queries are no longer available.</p>
<h2> Corpus</h2>
<p>IMDB critics corpus has been used in this example. Corpus is divided into a training and testing set. The testing set consists of 100 positive and 100 negative critiques, while the training set consists of 1000 positive critiques and 1000 negative including test critiques. The training is used as a database from which we extract occurrence frequency of certain phrases. The original idea of Turney's algorithm is to collect this data through an API (eg Google search) ie to collect data as how often a phrase usually appears next to the word. Since in the last few years, all search engines APIs limit the number of queries per day (they do not allow processing more than two files), it was necessary to implement own search engine version.</p>
<pre>
<code>
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
</code>
</pre>
<h2>Data structures and training and modeling algorithms</h2>
<p>Turney's algorithm runs through every test file. The text file is divided into separate words using the split() function and each word specifies the so-called <i>Part Of Speach</i> tag. As far as POS tags are defined, two word phrases have an adjective according to the following rules:</p>
<pre>
<code>
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
</code>
</pre>
<p>For each extracted phrase algorithm goes through all the train files and measure their coexistance with the words "great" and "poor". The coexistance is measured by calculating how many times the phrase and word (great or poor) occur at the distance x and less. Higher the x, greater the likelihood that the word does not apply to the phrase.</p>
<pre>
<code>
def near_operator(phrase, word, text):
    try:
        string= word+r'\W+(?:\w+\W+){0,500}?'+phrase+r'|'+phrase+r'\W+(?:\w+\W+){0,500}?'+word
        freq_phrase_near_word=(len(re.findall(string,text)))
        return freq_phrase_near_word
    except:
        return 0
</code>
</pre>
<h2>Evaluation</h2>
<p>Since there are many implementations of Turney's algorithm, but with external search, testing near operator has given some interesting results. When searched using a search engine, it is usual to search for a phrase and a word at a maximum distance of 10. When we implemented such a near operator, the accuracy of the algorithm was slightly over 50%. These are the measurements:</p>
<table>
  <tr>
    <th>Distance</th>
    <th>Accuracy</th>
  </tr>
  <tr>
    <td>max 10</td>
    <td>53%</td>
  </tr>
  <tr>
    <td>max 25</td>
    <td>60%</td>
  </tr>
  <tr>
    <td>max 50</td>
    <td>62%</td>
  </tr>
  <tr>
    <td>max 250</td>
    <td>63%</td>
  </tr>
</table>
<p>
We can notice that the accuracy increases with distance of the phrase and the corresponding word. Why is this happening? the number of files we search internally is far less than what we are searching through external search engines. So the search results are much more numerous. When we use a distance of up to 10, for most of the phrases we never find match, and they remain at a starting value of 0.01. Which means:</p>
<pre>
<code>
num(phrase near "great") = num(phrase near "poor")<br>
POLARITY(phrase)=log2(num(phrase near "great") * num("poor") / num(phrase near "poor") * num("great")) = num("poor") * num("great")
</code>
</pre>
<p> 
Since internal search does not match many phrases and words, the polarity is reduced to just the total number of words. Since the total number of words is the same for all phrases (searched in the same corpus), the algorithm lists all the phrases in the same category, negative or positive, depending on which number is greater. To solve this problem we had to extend the search. <br>
The question is: <b>"Is the search still relevant?"</b>
As we increased x (the phrase AROUND (x) word), there is a high chance of including words not coresponding phrase. However, the corpus we search by external search engines consists of data completely unrelated to the subject of our test corpus, so we have to insist on a relatively small x value.<br>
In this project, all the data we search are closely related to the subject of our test corpus so we can sacrifice distance from words without the loss of meaning. We can easily search for the probability that a phrase appears in the same critique as the word "great" or "poor".<br>
It would be ideal to search a large amount of relevant reviews (millions of data) to maximize the performance of the project. In the original version of the Turney algorithm applied to the same corpus, the accuracy of the algorithm is 66%, while in this project is 63%. We can conclude that we have not lost much of accuracy using an internal search engine. 
For the future, it would be interesting to see larger internal corpuses in order to evaluate their accuracy and determine whether this way can get more relevant results using Turney's algorithm.
</p>
