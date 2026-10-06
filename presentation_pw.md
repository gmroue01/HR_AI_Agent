Plan :

## How to test AI agent ?


1)  Le premier défi dans le testing d'IA est que les sorties de celle-ci ne sont pas de nature déterministes. Un LLM peut répondre à la même question à partir de sous-ensemble de réponses vraies.


**Exemple** : 

Question : *Quelle est la capitale de la Belgique ?* 
Réponses : *Bruxelles*, *La capital de la Belgique est Bruxelles*, *La capital est Bruxelles*,...

Ainsi, la définition d'une assertion tel que définie comme une proposition unique qu'on avance comme vraie, ne tient plus. 








## What's an agent ?

You use frameworks as deepeval,promptfoo, opik,trulens


How could we benchmark them ?
Let's build a use case :  HR Agent

Hr agent description : what, how,etc

What kind of test you build for ?

- Geval
- Tool calling
- ....



How to implement the test automation ?

- playwrigt
- selenium

-How do you optimize the test automation ? :

    - Juger le llm
    - mock le llm
    - metamorphisme test
    - statistic test
    - evaluation trajectoir de l'agent
    - 