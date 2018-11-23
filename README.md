# Turney-algorithm wih internal search
<p>Turney's algorithm with adaptation for the internal search of phrases beside the word. Reason for this kind of adaptation is that infinite number of search engine API queries are no longer available.</p>
<h2> Corpus</h2>
<p>IMDB critics corpus has been used in this example. Corpus is divided into a training and testing set. The testing set consists of 100 positive and 100 negative critiques, while the training set consists of 1000 positive critiques and 1000 negative with including test critiques. The training is used as a database from which we extract occurrence frequency of certain phrases. The original idea of Turney's algorithm is to collect this data through an API (eg Google search) ie to collect data as how often a phrase usually appears next to the word. Since in the last few years, all search engines APIs limit the number of queries per day (they do not allow processing more than two files), it was necessary to implement own search engine version.</p>
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
<p>Since there are many implementations of Turney's algorithm, but with external search, testing near operator has given some interesting results. When searched using a search engine, it is usual to search search for a phrase and a word at a maximum distance of 10. When we implemented such a near operator, the accuracy of the algorithm was slightly over 50%. These are the measurements:</p>
<table>
  <tr>
    <th>Udaljenost</th>
    <th>Tocnost</th>
  </tr>
  <tr>
    <td>maksimalno 10</td>
    <td>53%</td>
  </tr>
  <tr>
    <td>maksimalno 25</td>
    <td>60%</td>
  </tr>
  <tr>
    <td>maksimalno 50</td>
    <td>62%</td>
  </tr>
  <tr>
    <td>maksimalno 250</td>
    <td>63%</td>
  </tr>
</table>
<p>
We can notice that the accuracy increases with distance of the phrase and the corresponding word. Why is this happening? the number of files we search internally is far less than what we are searching through external search engines. So the search results are much more numerous. When we use a distance of up to 10, for most of the phrases we never find match, and they remain at a starting value of 0.01</p>
