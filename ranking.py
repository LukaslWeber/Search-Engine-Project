import numpy as np
from utils import preprocessing

'''
Function to calculate the TF-IDF score for the relevant documents
return the top 100 documents with the highest TF-IDF score as a list of tuples
'''

def TF_IDF(inverted_index, query, relevant_docs, doc_count):
    necessary_docs = 100
    if len(relevant_docs) < necessary_docs:
        necessary_docs = len(relevant_docs)
    query = preprocessing(query)
    query = query.split()
    IDF = np.zeros(len(query))
    for i in range(len(query)):
        IDF[i] = np.log10(doc_count/len(inverted_index[query[i]]))
    TF = np.zeros((len(relevant_docs), len(query)))
    for i,v in enumerate(query):
        doc_count = 0
        docs = inverted_index[v]
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