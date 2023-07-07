from File_loader import load_index
from Embedder import Embedder
from utils import preprocessing
import numpy as np
#Class for doing the ranking of the documents

class Ranker:
    def __init__(self, index_path: str, inverted_index_path:str, embedding_index_path: str, relevant_docs_count: int=100):
        self.index_db = load_index(index_path)
        self.inverted_index_db = load_index(inverted_index_path)
        self.doc_count = len(self.index_db)
        self.relevant_docs_count = relevant_docs_count
        self.load_embedding_index(embedding_index_path)	
    def rank(self, query: str, method: str) -> list:
        #TODO how to get the relevant documents for TD-IDF
        pass

    
    def load_embedding_index(self, embedding_index_path: str):
        """
        Load the embedding index
        :param embedding path
        """
        #TODO check if embedding was encoded with the some model 
        model_name = "roberta-base"
        embedding_index = load_index(embedding_index_path)
        # convert the embedding index to a numpy array
        self.id = []
        embedding = []
        for key, value in embedding_index.items():
            self.id.append(key)
            embedding.append(value)
        self.embeddings = np.stack(embedding, axis=0)
        self.embedder = Embedder(model_name)


    def embedding_ranking(self,query: str) -> list:
        query = preprocessing(query)
        query_embedding = self.embedder.embed(query)
        query_norm = np.linalg.norm(query_embedding)
        embeddings_norm = np.linalg.norm(self.embeddings, axis=1)
        normalized_query = query_embedding / query_norm
        normalized_dataset = self.embeddings / embeddings_norm[:, np.newaxis]
        cosine_similarity = np.dot(normalized_dataset, normalized_query)
        relevant_indecs = np.flip(np.argsort(cosine_similarity))
        sorted_docs = []
        for i in range(self.relevant_docs_count):
            id = relevant_indecs[i]
            sorted_docs.append([self.id[id], cosine_similarity[id]])
        return sorted_docs



    def TF_IDF(self, query: str, relevant_docs : list) -> list:
        """
        Calculate the TF-IDF score for the relevant documents
        :param query: the query string
        :param relevant_docs: the list of relevant documents
        :return: the top 100 documents with the highest TF-IDF score as a list of tuples (doc_id, score)
        """
        if len(relevant_docs) < self.relevant_docs_count:
            necessary_docs = len(relevant_docs)
        else:
            necessary_docs = self.relevant_docs_count
        query = preprocessing(query)
        query = query.split()
        IDF = np.zeros(len(query))
        for i in range(len(query)):
            IDF[i] = np.log10(self.doc_count/len(self.inverted_index[query[i]]))
        TF = np.zeros((len(relevant_docs), len(query)))
        for i,v in enumerate(query):
            docs = self.inverted_index[v]
            for doc in docs:
                doc_id = doc[0]
                if doc_id in relevant_docs:
                    TF[relevant_docs.index(doc_id), i] = len(doc[1])
        TF_IDF = TF @ IDF # for all the relevant documents
        relevant_indecs = np.flip(np.argsort(TF_IDF))
        sorted_docs = []
        for i in range(self.relevant_docs_count):
            id = relevant_indecs[i]
            sorted_docs.append([relevant_docs[id], TF_IDF[id]])
        return sorted_docs