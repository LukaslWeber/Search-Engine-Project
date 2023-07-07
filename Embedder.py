#Class for creating the embedding of the documents
from transformers import AutoTokenizer, AutoModelForMaskedLM, RobertaTokenizer, RobertaModel
import numpy as np
import math
class Embedder:
    def __init__(self, model_name : str, max_length : int = 512):
        if model_name == 'roberta-base':
            self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
            self.model = RobertaModel.from_pretrained(model_name)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.max_length = max_length
    def embed(self, text : str) -> np.array:
        """
        Embed a given text into a vector
        :param text: the text to embed already preprocessed
        :return: the embedding of the text
        """
        # splitting the text into sentences
        text_splitted = text.split()
        if len(text_splitted) > self.max_length:
            embeddings  = []
            split = math.ceil(len(text)/self.max_length)
            for i in range(split):
                start = i*self.max_length
                end = (i-1)*self.max_length
                if end > len(text_splitted):
                    end = len(text_splitted)
                sub_text = text_splitted[start:end]
                sub_text = ' '.join(sub_text)
                encoded_input = self.tokenizer(sub_text, return_tensors='pt')
                output = self.model(**encoded_input)
                embedding = output[0][0].detach().numpy() # the embedding of the first token CLS
                embeddings.append(embedding)
            return np.mean(embeddings, axis=0) # average of the embeddings
        else:
            encoded_input = self.tokenizer(text, return_tensors='pt')
            output = self.model(**encoded_input)
            embedding = output.last_hidden_state[0][0].detach().numpy()
            return embedding

if __name__ == '__main__':
    embedder = Embedder('roberta-base')
    text = 'I love to eat apples'
    embedding = embedder.embed(text)
    print(embedding.shape)