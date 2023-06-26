# Search-Engine
 Our Proposal for the "Modern Search Engines" Group project

## Creators:
 - Lukas Weber
 - Dana Rapp
 - Simon ...
 - Max ...

## Search Engine Structure
1. Crawler: Crawls the web for documents starting from the frontier
    - Store page-specific update frequencies in the frontier (Necessary?)!
    - Consider Access control (robots.txt)
    - Duplicate detection (exact and near duplicates)
      - [ ] Simhash
      - [ ] Autoencoders
3. Indexing: Saving the crawled content. Optimizing speed and performance in finding relevant documents for a search query so the search engine does not have to scan every document in the corpus & Matching query and document
     - Text representation
       - if necessary: Lower-Casing, Removing Stop words (exchanging . for <end> token)
       - Topic modelling (LDA)
         OR
       - Word Embeddings
         OR additionally
       - Contextual embedding (Transformer)
         - [ ] Transformer Memory as a Differentiable Search Index
4. Retrieval & Ranking: Process of reading the index and returning the desired results
    - PageRank
    - Conv-KNRM
    - Col-Bert
5. Search Engine Interface (Communicates with 3. and 4.)
    - Autocomplete
6. ((What about Fairness and Bias? (Part of the Slides about the project phase)))

## TODOs
- Plan
- Finish Crawler

- Choose Frontier
- Indexing Method
- Matching
- Ranking
- Interface

## Keep in Mind:
- Pipeline (processing) applied to all documents needs to be applied to the queries, too
