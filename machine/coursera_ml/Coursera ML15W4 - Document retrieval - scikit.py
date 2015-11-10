import pandas as pd
import numpy as np
from operator import itemgetter, attrgetter
from sklearn.feature_extraction.text import CountVectorizer
import nltk as nk

# nk.download()

people = pd.read_csv("people_wiki.csv")
people.describe()
people.head()
len(people)

obama = people[people['name'] == 'Barack Obama']
clooney = people[people['name'] == 'George Clooney']

count_vec = CountVectorizer(analyzer = 'word', tokenizer = None, preprocessor = None, stop_words = 'english') 
                           
obama_vec = count_vec.fit_transform(obama.text)                           
wc = zip(count_vec.get_feature_names(), np.asarray(obama_vec.sum(axis=0)).ravel())

# Sort
sorted(wc, key=itemgetter(1), reverse=True)

text = obama['text'].values[0]
text
tokens = nk.word_tokenize(text)
tokens
freq = nk.FreqDist(tokens)
freq.most_common()
