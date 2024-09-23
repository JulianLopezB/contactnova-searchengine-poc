import re
import unicodedata
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords

# nltk.download('punkt')
# nltk.download('stopwords')

# def preprocess_text(text):
     # Convert to lowercase
#     text = text.lower()
    
     # Remove accents
#     text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

    
     # Remove special characters, including x000d, but keep some punctuation marks
#     pattern=re.compile(r'_x000d_\n?',re.IGNORECASE)
#     text=pattern.sub('',text)

     # Remove special characters but keep some punctuation
 #    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', text)
    
     # # Remove special characters and digits
     # text = re.sub(r'[^a-zA-Z\s]', '', text)
    
     # Tokenize
#     tokens = word_tokenize(text,language='spanish')
    
     # Remove stopwords
#     stop_words = set(stopwords.words('spanish'))
#     tokens = [token for token in tokens if token not in stop_words]
    
     # Join tokens back into a string
#     preprocessed_text = ' '.join(tokens)
    
    # Convert to lowercase and remove extra whitespace
#     text = text.lower().strip()
#     text = re.sub(r'\s+', ' ', text)

#     return preprocessed_text

def preprocess_text(text):
    
    # Remove x000d
    pattern=re.compile(r'_x000d_\n?',re.IGNORECASE)
    text=pattern.sub('',text)
    # Remove special characters but keep some punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', text)
    
    # Convert to lowercase and remove extra whitespace
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)

    return text