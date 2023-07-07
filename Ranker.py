from File_loader import load_index
from utils import preprocessing
import numpy as np
#Class for doing the ranking of the documents

class Ranker:
    def __init__(self, index_path: str, inverted_index_path:str, relevant_docs_count: int=100):
        self.index_db = load_index(index_path)
        self.inverted_index_db = load_index(inverted_index_path)
        self.doc_count = len(self.index_db)
        self.relevant_docs_count = relevant_docs_count

    def rank(self, query: str, method: str) -> list:
        #TODO how to get the relevant documents for TD-IDF
        pass

    
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
        for i in range(necessary_docs):
            id = relevant_indecs[i]
            sorted_docs.append([relevant_docs[id], TF_IDF[id]])
        return sorted_docs