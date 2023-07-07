import time

def main():

	#create inverted index
	documents = ['Lorem ipsum dolor sit amet, consetetur ipsum sadipscing elitr, sed diam',
		'nonumy eirmod ipsum tempor invidunt ut labore et dolore magna aliquyam']

	preprocessed_documents = [doc.lower() for doc in documents]
	inverted_index = invert_index(preprocessed_documents)
	print(inverted_index)
        
	#create index with urls
	urls = ['https://www.tuebingen.de/', 'https://uni-tuebingen.de/']
    #preprocessing
	url_index = index(urls)
	print(url_index)


def index(urls):

	#url_index = {}
    url_index = {index: url for index, url in enumerate(urls)}
    return url_index


def invert_index(documents):
    
    inverted_index = {}
    
    for doc_id, string in enumerate(documents):
        terms = string.split()
        for position, term in enumerate(terms):
            if term not in inverted_index:
                inverted_index[term] = [[doc_id, [position]]]
            else:
                found = False
                for entry in inverted_index[term]:
                    if entry[0] == doc_id:
                        entry[1].append(position)
                        found = True
                        break
                if not found:
                    inverted_index[term].append([doc_id, [position]])
    return dict(sorted(inverted_index.items()))
	#TODO sorting takes up much time, do this more efficiently
	#output: {'term1': [[docID1, [pos1, pos2, ...]],[docID2, [pos4, pos7]], ...], 'term2': [[docID5, [pos1, pos2, ...]], ...}
	

if __name__ == '__main__':
    #start_time = time.time()
    main()
    #print("--- %s seconds ---" % (time.time() - start_time))
    