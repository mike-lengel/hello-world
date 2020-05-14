from bs4 import BeautifulSoup
import urllib3
from collections import defaultdict
from string import punctuation
from heapq import nlargest
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#nltk.download()

html=['<html><heading style="font-size:20px"><i>This is the title<br><br></i></heading>',
     '<body><b>This is the body</b><p id="para1">This is para1<a href="www.google.com">Google</a></p>',
     '<p id="para2">This is para 2</p></body></html>']
html=''.join(html)

soup = BeautifulSoup(html,"html.parser")
print(soup.prettify())

class FrequencySummarizer:
    """
    A class used to determine the frequency of words in each sentence of a text.

    ...

    Attributes
    -----------
    stopwords : list(str)
        a list of common English words to remove from frequency counts
    min_cut : float
        ignore words with normalized frequency less than this (default 0.1)
    max_cut : float
        ignore words with normalized frequency greater than this (default 0.9)

    Methods
    ----------
    _compute_frequencies(sent_word) -> defaultdict
        Input : list of list of words for each sentence
        Output: dictionary of words and their (normalized) frequency in the list

    summarize()

    """
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english')+list(punctuation))
    
    def _compute_frequencies(self, sent_word : list) -> defaultdict(int):
        freq = defaultdict(int)
        #use defaultdict to allow creation of new keys when a referenced one doesn't already exist
        
        #get a count of occurences or each word in sentenceList ignoring stopwords
        for s in sent_word:
            for word in s:
                if word not in self._stopwords:
                    freq[word] +=1

        #get the highest frequency of any word in list
        m = float(max(freq.values()))

        #for Debug purposes, print this value out
        logging.debug("The following is the frequency list ignoring stopwords:\n"+str(freq))
        logging.debug("The maximum frequency was "+str(m))

        #TODO: normalize the frequency
        for w in list(freq.keys()):
            freq[w] = freq[w]/m

            if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
                del freq[w]

        logging.debug("The following is the adjusted frequency list ignoring stopwords:\n" + str(freq))

        return freq
    
    def summarize(self, text : str, n : int):
        sentencesList = sent_tokenize(text)
        assert n <= len(sentencesList)
        wordsInSentencesList = [word_tokenize(s.lower()) for s in sentencesList]

        self._freq = self._compute_frequencies(wordsInSentencesList)

        ranking = defaultdict(int)

        for i,sent in enumerate(wordsInSentencesList):
            for w in sent:
                if w in self._freq:
                    ranking[i] += self._freq[w]

        sentence_index = nlargest(n, ranking, key=ranking.get)

        return [sentencesList[j] for j in sentence_index]

#TODO: Create a simple test for _compute_frequencies
summary = FrequencySummarizer()
print(summary.summarize("In the beginning was the Word, and the Word was with God, and the Word was fully God. The Word was with God in the beginning. All things were created by him, and apart from him not one thing was created that has been created. In him was life, and the life was the light of mankind. And the light shines on in the darkness, but the darkness has not mastered it. A man came, sent from God, whose name was John. He came as a witness to testify about the light, so that everyone might believe through him. He himself was not the light, but he came to testify about the light. The true light, who gives light to everyone, was coming into the world. He was in the world, and the world was created by him, but the world did not recognize him. He came to what was his own, but his own people did not receive him. But to all who have received him - those who believe in his name - he has given the right to become God's children - children not born by human parents or by human desire or a husband's decision, but by God. Now the Word became flesh and took up residence among us. We saw his glory - the glory of the one and only, full of grace and truth, who came from the Father. John testified about him and shouted out, 'This one was the one about whom I said, 'He who comes after me is greater than I am, because he existed before me.'' For we have all received from his fullness one gracious gift after another. For the law was given through Moses, but grace and truth came about through Jesus Christ.",3))

import urllib.request

def get_only_text_from_url(url,keytag : str):
    page = urllib.request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(page, features="html.parser")

    #TODO: figure out how to unbreak this code.  It is only grabbing article headlines
    text = ' '.join(map(lambda p:p.text, soup.find_all(keytag)))

    soup2 = BeautifulSoup(text, features="html.parser")
    text =' '.join(map(lambda p:p.text, soup2.find_all('p')))

    return soup.title.text, text

someUrl = "https://www.washingtonpost.com/nation/2020/05/14/coronavirus-update-us/#link-R76FCK4U4VEYLCRF2VTOQRQYM4"
keytag = 'article'
textOfUrl = get_only_text_from_url(someUrl,keytag)
print(textOfUrl)

fs = FrequencySummarizer()
summary = fs.summarize(textOfUrl[1],3)

print("Summary of " + textOfUrl[0] +"\n"+summary)