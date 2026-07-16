# Project configuration

# Github:

I create a github repository to save the project and have a look on the project progress.

The repository is https://github.com/gmroue01/HR_AI_Agent

Basics commande are : 

```bash
git init

git remote add origin https://github.com/gmroue01/HR_AI_Agent.git

git branch -M main

``` 

I choose the MIT License and the repository is initially private.

I add a readMe and .gitignore



## .gitignore

.gitignore allow to push some confidential, heavy or useless files in the github repository.


It blocks these files/folders :
    
    - .env
    - venv 

# Virtual Environnement

I create a virtual environnement from python venv module. I do so to prevent global package clashes.


# Dependencies 

The detail list of library/dependencies is detailled in 'requirements.txt'.

I develop in Python 3.13.2.


To resume, I install :

- Groq (source : https://groq.com/)
- dotenv (source: https://pypi.org/project/python-dotenv/)


## Groq

Groq is an AI technology compagny that designs specialized chips and hardware for fast, low-cost AI inference.

Groq shall provide us the access to a various choices of LLM models without pay (rate limits exists).

### Instalation 

Groq is very easy to install.
```python
pip install groq
```
### Configuration 

Groq requires an API Key to authenticate requests.

1. Get API Key from "https://console.groq.com/keys"
2. Create '.env' file at the project root (.env)
3. Add the following variable : 
```
GROQ_API_KEY =your_api_key_here
```
4. Load it in the code : 
```python
import os
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")

```

The API_KEY is referenced in the .gitignore.


## dotenv

python-dotenv reads key-value pairs from .env file and can set them as environnement variables.

I use it to return API_KEY for Groq Service.

### Installation 

python-dotenv is very easy to install.

``` 
pip install python-dotenv
```



## FastAPI

FastAPI is a modern, fast, web framework for building APIS with Python based on standard Python type hints.

I use it to deploy an backend API that allow to communicate with a database.


### Installation

FastAPI is very easy to install.

```bash
pip install "fastapi[standard]"
```


## PyDantic

Pydantic is a data validation library for Python. 

I use it to combine with FastApi that is based on type hints. PyDantic enable to construct schema type validation.


### Installation 

```bash

pip install pydantic

```

## Typing


Typing is a module and implements Python's gradual typing system. It allows developpers to add type hints to their code, which can help with code clarity, maintainability and error detection during development.

Typing module is build-in Python since Python 3.5 .

No installation required.

## Python SQLite3

Python SQLite3 module is used to integrate the SQLite database with Python.
It is a standardized Python DBI API 2.0 and provides a straightforward and simple-to-use interface for interacting with SQLite databases. 

Python SQLite3 is build-in in Python since Python 2.5.


## Uvicorn 

uvicorn is a *asynchronous server gateway interface*, which is intented to provide a standard interface between async-capable Python web servers, frameworks, and application.

Uvicorn is sponsored by FastApi and support HTTP/1.1 and WebSockets.

### Installation 

uvicorn is easy to install.

```bash
pip install uvicorn
```

### Run the interface

To run the interface, we need this command :

```bash
uvicorn main:app
```

As `main:app` refers to a `main.py` that runs the interface application.

Let's see example for documentations (https://uvicorn.dev/#quickstart) : 

```python
# main.py
async def app(scope, receive, send):
    assert scope['type'] == 'http'

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', b'text/plain'),
            (b'content-length', b'13'),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello, world!',
    })

```

```bash
uvicorn main:app
```


## ChromaDB

ChromaDB is an open-source data infrastructure for AI. It enables to build RAG systems including the embeddings, retrieval algorithms.


### Installation

```bash
pip install chromadb
```

## pdfplumber

pdfplumber plumb a PDF for detailed information about each text character, rectangle, and line. 


### Installation

```bash

pip install pdfplumber
``` 

## streamlit

Streamlit is an open-source Python framework for data scientists and AI/ML engineers to deliver dynamic data apps with only a few lines of code. Build and deploy powerful data apps in minutes.


## Installation 

```bash

pip install streamlit

```

## Openpyxl

openpyxl is a Python library to read/write Excel 2010 .xlsx file.

### Installation

```bash

pip install openpyxl

```
## DeepEval

deepeval is an open-source library providing a complete framework to test LLM system, RAG and hallucinations

### Installation

```bash
pip install -U deepeval
```