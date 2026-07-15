# RAG System : 

Retrieval-Augmented Generation is a way to make AI answers more reliable by combining searching for relevant information and then generating a response. 

The relevant information is stored into documents (PDF File, Text file, Excel File,...) or databases.

In this document, we present the main components of RAG and how we implement them.

`ChromaDB` is the open-source library for RAG system. We use it in this project.

The client is instantiates once at the script [`chroma_client.py`](../rag/chroma_client.py) and stores in the `client` variable, providing a shared connection to the API service and the set of tools provided. 


The on-disk vector database store located at `CHROMA_PATH`.

## External knowledge Source : 

The external knowledge source is stored into [`../data/`](../data/).

In this project, we retrieve this type of source data : 

 -  ['hr_policies`](../data/hr_policies/) : Policies (PDF File) of the compagny about expenses.
 -  [`secret_projects`](../data/hr_policies/) : Confidential projects only accessible by the HR (PDF File).
 -  [`salary_grid`](../data/salary_grids) : Salary grid of the company (Excel File).

## Text Chunking and Preprocessing :

The large documents must be break into smaller, manageable chunks and cleans it for consistency.


**chunk_test()** function implement the *fixed-size chunking*.
The logic behind is to divide the text into overlapping segments, utilizing a predefined window size. This method ensures that the end of the one chunk overlaps with the beginning of the next and maintining the contextual integrity of the information.











