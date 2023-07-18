from File_loader import load_index
from Embedder import Embedder
from utils import preprocessing
import numpy as np
import os
#Class for doing the ranking of the documents

class Ranker:
    def __init__(self, index_path: str, inverted_index_path:str, embedding_index_path: str, results_path: str, relevant_docs_count: int=100, ):
        self.index_db = load_index(index_path)
        self.inverted_index_db = load_index(inverted_index_path)
        self.doc_count = len(self.index_db)
        if self.doc_count < relevant_docs_count:
            self.relevant_docs_count = self.doc_count
        else:
            self.relevant_docs_count = relevant_docs_count
        self.load_embedding_index(embedding_index_path)
        if not self.check():
            raise ValueError("The indecies do not have the same length")
        self.embedder = Embedder('bert-base-uncased') #must be set to the same model as the one used for the embedding index
        self.rank_method = "BM25" #TODO: change to TF-IDF
        self.results_path = results_path
        self.b = 0.75
        self.k1 = 1.2
        self.calculate_avgdl() #TODO: calculate the average document length


    def calculate_avgdl(self):
        """
        Calculate the average document length
        """
        avgdl = 0
        for key, value in self.index_db.items():
            avgdl += value[1]
        self.avgdl = avgdl/len(self.index_db)


    def check(self)-> bool:
        """
        Check if all the indecies are loaded correctly
        :return: True if the index is loaded, False otherwise
        """
        index_len = len(self.index_db)
        embedding_number = self.embeddings.shape[0]
        ids = len(self.id)
        print("Index length: ", index_len)
        print("Embedding number: ", embedding_number)
        print("ID length: ", ids)
        if index_len == embedding_number and index_len == ids:
            return True
        else:
            return False

    def rank(self, query: str) -> list:
        #TODO how to get the relevant documents for TD-IDF
        #just use and 

        if self.rank_method == "embedding":
            sorted_docs = self.embedding_ranking(query)
        else:
            relevant_docs = self.query_union(query)
            if self.rank_method == "BM25":
                sorted_docs = self.BM25(query, relevant_docs)
            if self.rank_method == "TF-IDF":
                sorted_docs = self.TF_IDF(query, relevant_docs)
        self.save_results(sorted_docs, query)
        return [self.index_db[result[0]][0] for result in sorted_docs]
        #TODO return ordere list of links

    
    def load_embedding_index(self, embedding_index_path: str):
        """
        Load the embedding index
        :param embedding path
        """
        #TODO check if embedding was encoded with the some model
        embedding_index = load_index(embedding_index_path)
        print("Embedding index loaded")
        print(embedding_index)
        # convert the embedding index to a numpy array
        self.id = []
        embedding = []
        for key, value in embedding_index.items():
            self.id.append(key)
            embedding.append(value)
        self.embeddings = np.stack(embedding, axis=0)

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


    def query_union(self,query: str) -> list:
        """
        Select the documents that are relevant for the query
        :param query: the query string
        :return: the list of relevant documents
        """
        query = preprocessing(query)
        query = query.split()
        relevant_words = []
        for word in query:
            if word in self.inverted_index_db.keys():
                relevant_words.append(self.inverted_index_db[word])
        relevant_docs = []
        for word in relevant_words:
            for doc in word:
                relevant_docs.append(doc[0])
        return sorted(set(relevant_docs))


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
            print(id)
            print(self.index_db[self.id[id]][0])
            print(cosine_similarity[id])
            sorted_docs.append([self.id[id], cosine_similarity[id]])
        return sorted_docs


    def save_results(self, results: list, query: str):
        """
        Save the results in the given path
        :param results: the list of results
        :param query: the query string
        """
        file_name = query.replace(" ", "_") + "_"+ self.rank_method+ ".txt"
        file_path = os.path.join(self.results_path, file_name)
        with open(file_path, "w") as f:
            for i,result in enumerate(results):
                f.write(str(i) + "\t"+ str(self.index_db[result[0]][0]) + "\t" + str(result[1]) + "\n")
        


    def BM25(self, query: str, relevant_docs : list) -> list:
        """
        Calculate the BM25 score for the relevant documents
        :param query: the query string
        :param relevant_docs: the list of relevant documents
        :return: the top 100 documents with the highest BM25 score as a list of tuples (doc_id, score)
        """
        #TODO
        if len(relevant_docs) < self.relevant_docs_count:
            necessary_docs = len(relevant_docs)
        else:
            necessary_docs = self.relevant_docs_count
        query = preprocessing(query)
        query = query.split()
        IDF = np.zeros(len(query))
        for i in range(len(query)):
            n_q = len(self.inverted_index_db[query[i]])
            IDF[i] = np.log(((self.doc_count-n_q+0.5)/(n_q+0.5))+1)
        TF = np.zeros((len(relevant_docs), len(query)))
        for i,v in enumerate(query):
            docs = self.inverted_index_db[v]
            for doc in docs:
                doc_id = doc[0]
                if doc_id in relevant_docs:
                    f = len(doc[1])
                    D = self.index_db[doc_id][1] # TODO
                    TF[relevant_docs.index(doc_id), i] = (f * (self.k1+1))/(f+self.k1*(1-self.b+self.b*(D/self.avgdl)))
        BM25 = TF @ IDF # for all the relevant documents
        relevant_indecs = np.flip(np.argsort(BM25))
        sorted_docs = []
        for i in range(necessary_docs):
            id = relevant_indecs[i]
            sorted_docs.append([relevant_docs[id], BM25[id]])
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
        TF = np.zeros((len(relevant_docs), len(query)))
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
    path = 'data_files_bert_2'
    index = os.path.join(path, 'forward_index.joblib')
    index_inverted = os.path.join(path, 'inverted_index.joblib')
    index_embedding ="/home/franksim/Search-Engine-Project/data_files_bert_2/bert-base-uncased temp_embedding_index_pre.joblib" #os.path.join(path, 'bert-base-uncased_temp_embedding_index.joblib')
    result_path = os.path.join(path, 'results')
    ranker = Ranker(index, index_inverted, index_embedding, result_path, 100)
    ranker.rank("food and drinks")
    ranker.rank("tübingen attractions")
    #ranker.rank_method = "TF-IDF"
    #ranker.rank("food and drinks")
    #ranker.rank("tübingen attractions")

    #ranker.rank_method = "TF-IDF"
    #ranker.rank("food and drinks")
    