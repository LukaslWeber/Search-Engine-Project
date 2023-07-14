from File_loader import load_index
from Embedder import Embedder
from utils import preprocessing
import numpy as np
import os
#Class for doing the ranking of the documents

class Ranker:
    def __init__(self, index_path: str, inverted_index_path:str, embedding_index_path: str, relevant_docs_count: int=100):
        self.index_db = load_index(index_path)
        self.inverted_index_db = load_index(inverted_index_path)
        self.doc_count = len(self.index_db)
        if self.doc_count < relevant_docs_count:
            self.relevant_docs_count = self.doc_count
        else:
            self.relevant_docs_count = relevant_docs_count
        self.load_embedding_index(embedding_index_path)
    def rank(self, query: str) -> list:
        #TODO how to get the relevant documents for TD-IDF
        #just use and 
        relevant_docs = self.document_selection(query)
        print(relevant_docs)
        matches = self.listintersection(relevant_docs[0], relevant_docs[1])
        print(matches)
        result = self.TF_IDF(query, matches)
        print(result)
        pass

    
    def load_embedding_index(self, embedding_index_path: str):
        """
        Load the embedding index
        :param embedding path
        """
        #TODO check if embedding was encoded with the some model 
        model_name = "bert-base-uncased"
        embedding_index = load_index(embedding_index_path)
        # convert the embedding index to a numpy array
        self.id = []
        embedding = []
        for key, value in embedding_index.items():
            self.id.append(key)
            embedding.append(value)
        self.embeddings = np.stack(embedding, axis=0)
        self.embedder = Embedder(model_name)

    def document_selection(self, query: str) -> list:
        """
        Select the documents that are relevant for the query
        :param query: the query string
        :return: the list of relevant documents
        """
        query = preprocessing(query)
        query = query.split()
        relevant_docs = []
        for word in query:
            if word in self.inverted_index_db.keys():
                relevant_docs.append(self.inverted_index_db[word])
        return relevant_docs

    def listintersection(self,lista, listb):
        pointerA=0
        pointerB=0
        matches =[]
        print(lista)
        print(listb)
        while pointerA< len(lista) and pointerB< len(listb):
            if lista[pointerA][0]==listb[pointerB][0]:
                matches.append(lista[pointerA][0])
                pointerB+=1
                pointerA+=1
            elif lista[pointerA][0]<listb[pointerB][0]:
                pointerA+=1
            elif lista[pointerA][0]>listb[pointerB][0]:
                pointerB+=1
        return matches 

    def embedding_ranking(self,query: str) -> list:
        #query = preprocessing(query)
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
            print(id)
            print(self.index_db[self.id[id]][0])
            print(cosine_similarity[id])
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
            IDF[i] = np.log10(self.doc_count/len(self.inverted_index_db[query[i]]))
        TF = np.zeros((necessary_docs, len(query)))
        for i,v in enumerate(query):
            docs = self.inverted_index_db[v]
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
    

if __name__ == "__main__":
    path = 'data_files'
    index = os.path.join(path, 'temp_forward_index.joblib')
    index_inverted = os.path.join(path, 'temp_inverted_index.joblib')
    index_embedding = os.path.join(path, 'temp_embedding_index.joblib')
    ranker = Ranker(index, index_inverted, index_embedding)
    ranker.embeddings = np.load(os.path.join(path, 'temp_embed_bert_base_uncased_preprocessing.npy'))
    #ranker.embeddings = np.load(os.path.join(path, 'temp_embed_bert_base_uncased.npy'))
    res = ranker.embedding_ranking("tübingen attractions")
    ranker.rank("tübingen attractions")
    #print(res)
    #query = "What is the capital of Germany?"
    #print(ranker.embedding_ranking(query))