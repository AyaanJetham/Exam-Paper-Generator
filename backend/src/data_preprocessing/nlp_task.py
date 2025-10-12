from nltk.corpus import stopwords
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

def clean_text(text):
    nltk.download('punkt_tab')
    nltk.download("stopwords")
    nltk.download('wordnet')
    stop_words = set(stopwords.words('english'))
    #  replacing more than 1 whitespace character to one whitespace and remove unwanted characters
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\\u[a-fA-F0-9]{4}", "", text)
    text = re.sub(r"Week \d+:", "", text)

    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word.lower() not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return " ".join(tokens)

