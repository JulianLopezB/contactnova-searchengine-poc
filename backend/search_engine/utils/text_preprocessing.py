import re
import unicodedata
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
     # Convert to lowercase
     text = text.lower()
    
     # Remove accents
     text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

    
     # Eliminar caracteres especiales, incluyendo x000d, pero mantener algunos signos de puntuación
     patron=re.compile(r'_x000d_\n?')
     text=patron.sub('',text)
     text = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ\s.,!?]', ' ', text)
     
    
     # # Remove special characters and digits
     # text = re.sub(r'[^a-zA-Z\s]', '', text)
    
     # Tokenize
     tokens = word_tokenize(text)
    
     # Remove stopwords
     stop_words = set(stopwords.words('spanish'))
     tokens = [token for token in tokens if token not in stop_words]
    
     # Join tokens back into a string
     preprocessed_text = ' '.join(tokens)
    
    # Convert to lowercase and remove extra whitespace
     text = text.lower().strip()
     text = re.sub(r'\s+', ' ', text)

     return preprocessed_text
