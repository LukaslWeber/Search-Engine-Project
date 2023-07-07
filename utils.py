import nltk
from nltk.corpus import stopwords
from string import punctuation
nltk.download('stopwords')
stopwords = set(stopwords.words('english'))
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

'''
Function is performing preprocessing on the text and the query
Steps:
lower case
stop word removal 
lemmatization
'''
#TODO: replace umlaute, alle satzzeichen raus


def preprocessing(text):
    text = text.lower()

    # Tokenize the text into individual words
    words = text.split()

    # Remove stopwords from the tokenized words
    words = [word for word in words if word not in stopwords]       
    
    words = [word for word in words if word not in punctuation]

    # Lemmatize each word in the list
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    
    # Join the lemmatized words back into a string
    lemmatized_text = ' '.join(lemmatized_words)

    return lemmatized_text
