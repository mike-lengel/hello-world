import requests
import urllib.request
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
from math import log
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class FrequencySummarizer:
    def __init__(self,min_cut=0.1,max_cut=0.9):
        # class constructor - takes in min and max cutoffs for 
        # frequency
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english') +
                              list(punctuation) +
                              [u"'s",'"'])
        # notice how the stopwords are a set, not a list. 
        # its easy to go from set to list and vice-versa
        # (simply use the set() and list() functions) - 
        # but conceptually sets are different from lists
        # because sets don't have an order to their elements
        # while lists do
    
    def _compute_frequencies(self,word_sent,customStopWords=None):
        freq = defaultdict(int)
        # we have encountered defaultdict objects before
        if customStopWords is None:
            stopwords = set(self._stopwords)
        else:
            stopwords = set(customStopWords).union(self._stopwords)
        for sentence in word_sent:
            for word in sentence:
                if word not in stopwords:
                    freq[word] += 1
        m = float(max(freq.values()))
        for word in list(freq.keys()):
            freq[word] = freq[word]/m
            if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
                del freq[word]
        return freq
    
    def extractFeatures(self,article,n,customStopWords=None):
        # The article is passed in as a tuple (text, title)
        text = article[0]
        # extract the text
        title = article[1]
        # extract the title
        sentences = sent_tokenize(text)
        # split the text into sentences
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        # split the sentences into words 
        self._freq = self._compute_frequencies(word_sent,customStopWords)
        # calculate the word frequencies using the member function above
        if n < 0:
            # how many features (words) to return? IF the user has
            # asked for a negative number, this is a sign that we don't
            # do any feature selection - we return ALL features
            # THis is feature extraction without any pruning, ie no
            # feature selection (beyond simply picking words as the features)
            return nlargest(len(self._freq_keys()),self._freq,key=self._freq.get)
        else:
            # if the calling function has asked for a subset then
            # return only the 'n' largest features - ie here the most
            # important words (important == frequent, barring stopwords)
            return nlargest(n,self._freq,key=self._freq.get)
        # let's summarize what we did here. 
    
    def extractRawFrequencies(self, article):
        # very similar, except that this method will return the 'raw'
        # frequencies - literally just the word counts
        text = article[0]
        title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        freq = defaultdict(int)
        for s in word_sent:
            for word in s:
                if word not in self._stopwords:
                    freq[word] += 1
        return freq
    
    def summarize(self, article,n):
        text = article[0]
        title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i,sentence in enumerate(word_sent):
            for word in sentence:
                if word in self._freq:
                    ranking[i] += self._freq[word]
        sentences_index = nlargest(n,ranking,key=ranking.get)

        return [sentences[j] for j in sentences_index]


def getAllBlogArticles(url,links):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    soup = BeautifulSoup(response,features="html.parser")
    for a in soup.findAll('a'):
        try:
            url = a['href']
            title = a['title']
            if title == "Older posts":
                print(title + ": "+url)
                links.append(url)
                getAllBlogArticles(url,links)
        except:
            title =""
    return

def getBlogText(testUrl,token):
    response = requests.get(testUrl)
    soup = BeautifulSoup(response.content,features="html.parser")
    page = str(soup)
    title = soup.find("title").text
    mydivs = soup.findAll("div",{"class":token})
    text = ''.join(map(lambda p:p.text,mydivs))
    return text,title

#testURL = "https://www.dividenddiplomats.com/expected-dividend-increases-in-may-hopefully/"
contentToken = "entry-content"
#testArticle = getBlogText(testURL,contentToken)
#print(testArticle)

blogUrl = "https://www.dividenddiplomats.com/"
contentToken = "entry-content"
links=[]
getAllBlogArticles(blogUrl,links)
print(links)

blogPosts = {}
for link in links:
    blogPosts[link] = getBlogText(link,contentToken)

documentCorpus = []
for onePost in blogPosts.values():
    documentCorpus.append(onePost[0])
    print(onePost[1])

vectorizer = TfidfVectorizer(max_df=0.5,min_df=2,stop_words='english')
X = vectorizer.fit_transform(documentCorpus)
km = KMeans(n_clusters = 5, init = "k-means++", max_iter=100, n_init = 1, verbose = True)
km.fit(X)

keywords={}
for i,cluster in enumerate(km.labels_):
    oneDocument = documentCorpus[i]
    fs = FrequencySummarizer()
    summary = fs.extractFeatures((oneDocument,""),100,[u"according",u"like",u"new",u"one",u"year",u"first",u"last"])
    
    if cluster not in keywords:
        keywords[cluster] = set(summary)
    else:
        keywords[cluster] = keywords[cluster].intersection(set(summary))
