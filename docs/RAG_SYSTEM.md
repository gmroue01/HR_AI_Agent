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

 -  [`hr_policies`](../data/hr_policies/) : Policies (PDF File) of the compagny about expenses.
 -  [`confidential_projects`](../data/confidential_projects/) : Confidential projects only accessible by the HR (text files).
 -  [`salary_grid`](../data/salary_grids) : Salary grid of the company (Excel File).

## Text Chunking and Preprocessing :

The large documents must be break into smaller, manageable chunks and cleans it for consistency.


**chunk_test()** function operates this task and implements the *fixed-size chunking*.
The logic behind this is to divide the text into overlapping segments, utilizing a predefined window size. This method ensures that the end of one chunk overlaps with the beginning of the next and preserving the contextual integrity of the information.


**ingest_documents()** applies the chunking algorithm to all the documents. 
Each document is added to a `Collection`, which is the fundamental unit of storage and querying in `ChromaDB`.

The `Collection` will **embed** them by using its default embedding function.

**ingest_documents()**  accepts  `.txt` and `.pdf` file.
If the document is not a `.txt` file, it must be passed into a method that extracts its content into plain text.

This method is currently : 

- **extract_pdf_text()**

`extract_pdf_text()` also cleans the text it gets from `pdfplumber` : some fonts's bullet glyph can't be mapped to a unicode character, and `pdfplumber` leaves the raw PDF glyph id (`(cid:127)`) in the text instead. This would end up stored as-is in `ChromaDB` and reach the LLM as noise, so it is replaced by `-` right after extraction.

`chunk_test()` never cuts a chunk in the middle of a word. It extends the chunk end to the next whitespace, so a chunk always ends with a complete word (a chunk can therefore be slightly longer than `chunk_size`). Without this, a fixed-size cut could land mid-word (e.g. splitting "Traffic fines" into "Traffic fi" / "nes" across two chunks), which is meaningless once embedded on its own.

## Vector databases :

The embedding vector is stored in a [`chroma_db`](../chroma_db/) folder.

`chroma.sqlite3` is the database containing the vector.

There is also a folder containing the  **HNSW** (*Hierarchical Navigable Small World*) vector index,
, which is the foundation of the similarity search.




## Similarity search and retrieval :

**search_hr_documents_logic()** implements the similarity search logic in the [`document_service.py`](../backend/services/document_service.py) script.

Essentialy, the function calls the `collection.query()` method from `ChromaDB` and returns the most results based to the user's query.


The function returns a dictionary with the relevant text from the retrieved documents and their associated metadata.


## Prompt Augmentation Layer : 

In order to combine retrieved chunks with user's query and provide context to the LLM, the [`TOOLS_SCHEMA`](../tools/schemas.py) and the [`dispatcher.py`](../tools/dispatcher.py) scripts enalble to connection between the retrieval system and the agent.

[`chatbot_core.py`](../chatbot_core.py) script orchestrates the agent's tool call.

