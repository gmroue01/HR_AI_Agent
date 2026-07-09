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



