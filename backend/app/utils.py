from bs4 import BeautifulSoup
import os
import pandas as pd
import re
from collections import Counter
import fasttext
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()



def extract_text_from_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    
    # Get text and handle encoding
    text = soup.get_text(separator=' ', strip=True)
    return text


def preprocess_text(html_content,keep_accent:bool=True):
    # Remove HTML tags
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    # Remove special characters but keep some punctuatio
    if keep_accent:
        text = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ\s.,!?]', ' ', text)        
    else:
        text = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', text)
    # Convert to lowercase and remove extra whitespace
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)

    return text


def get_preprocessed_texts():
    # Load and filter
    file_path = os.getenv("EXCEL_FILE_PATH")
    df = pd.read_excel(file_path)
    df = df[df['obsoleto'].isna()]
    df = df[df['revisado'] == 's']
    df = df.reset_index(drop=True)
    # process
    texts = []
    for _, row in df.iterrows():
        pregunta_html = str(row['pregunta'])
        respuesta_html = str(row['respuesta'])
        
        pregunta_text = preprocess_text(pregunta_html)
        respuesta_text = preprocess_text(respuesta_html)
        
        full_text = pregunta_text + ' ' + respuesta_text
        metadata = {
            'id': int(row['id']),
            'pregunta': pregunta_html,
            'respuesta': respuesta_html,
            'grupo': row['grupo'],
            'tema': row['tema']
        }
        texts.append(full_text)
    
    return texts 

class Analysis:
    '''
    model_path : 
         ->.env
    '''
    def __init__(self, model_path):
        self.mode_path=model_path
        self.model = fasttext.load_model(model_path)
        self.preprocess_text=preprocess_text
        self.keep_accent : bool =False

    def get_language(self):
        df = self._load_text()
        n_gl = 0
        total_palabras = 0
        for _, row in df.iterrows():
            pregunta_text = self.preprocess_text(str(row['pregunta']),self.keep_accent)
            respuesta_text = self.preprocess_text(str(row['respuesta']),self.keep_accent)
            full_text = pregunta_text + ' ' + respuesta_text
            total_palabras += self.contar_palabras(full_text)
            if self._is_galician(respuesta_text,self.mode_path):
                n_gl += 1
        perct = n_gl / len(df)
        print(f'El total de documentos en gallego es: {perct*100:.2f}%')
        print(f'El número total de palabras en los textos procesados es: {total_palabras}')

    @staticmethod
    def _load_text():
        file_path = os.getenv("EXCEL_FILE_PATH")
        df = pd.read_excel(file_path)
        df = df[df['obsoleto'].isna()]
        df = df[df['revisado'] == 's']
        return df.reset_index(drop=True)
    
    def contar_palabras(self,texto):
        return len(texto.split())

    def _is_galician(self, text: str, model_path: str, threshold: float = 0.0):
        prediction = self.model.predict(text, k=1)
        label, confidence = prediction[0][0], prediction[1][0]
        return label in ['__label__gl','__label__pt'] and confidence >= threshold
    
    def get_distribution(self):
        df=self._load_text()
        distribution=[]
        for _,row in df.iterrows():

            pregunta_text = self.preprocess_text(str(row['pregunta']),self.keep_accent)
            respuesta_text = self.preprocess_text(str(row['respuesta']),self.keep_accent)
            full_text = pregunta_text + ' ' + respuesta_text
            distribution.append(self.contar_palabras(full_text))
        return distribution
    
    def plot_distribution(self):
        distribution = self.get_distribution()
        
        plt.figure(figsize=(10, 6))
        sns.histplot(distribution, kde=True)
        plt.title('Distribution of Word Count per Text')
        plt.xlabel('Number of Words')
        plt.ylabel('Frequency')
        plt.show()

        print(f"Distribution statistics:")
        print(f"Minimum: {min(distribution)}")
        print(f"Maximum: {max(distribution)}")
        print(f"Average: {sum(distribution) / len(distribution):.2f}")
        print(f"Median: {sorted(distribution)[len(distribution)//2]}")

    def plot_top_words(self, n:int=20):
        df = self._load_text()
        all_words = []
        for _, row in df.iterrows():
            pregunta_text = self.preprocess_text(str(row['pregunta']))
            respuesta_text = self.preprocess_text(str(row['respuesta']))
            all_words.extend(pregunta_text.split() + respuesta_text.split())
        
        word_freq = Counter(all_words)
        top_words = dict(word_freq.most_common(n))
        
        plt.figure(figsize=(12, 6))
        plt.bar(top_words.keys(), top_words.values())
        plt.title(f'Top {n} Most Frequent Words')
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def plot_group_distribution(self):
        df = self._load_text()
        group_counts = df['grupo'].value_counts()
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=group_counts.index, y=group_counts.values)
        plt.title('Distribution of Texts by Group')
        plt.xlabel('Group')
        plt.ylabel('Number of Texts')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def plot_word_count_by_group(self):
        df = self._load_text()
        df['word_count'] = df.apply(lambda row: self.contar_palabras(self.preprocess_text(str(row['pregunta'])) + ' ' + self.preprocess_text(str(row['respuesta']))), axis=1)
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='grupo', y='word_count', data=df)
        plt.title('Word Count Distribution by Group')
        plt.xlabel('Group')
        plt.ylabel('Word Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()


if __name__=='__main__':

    analis=Analysis(os.getenv('LANG_MODEL_PATH'))
    analis.plot_word_count_by_group()


