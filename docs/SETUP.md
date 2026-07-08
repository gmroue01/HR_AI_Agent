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
