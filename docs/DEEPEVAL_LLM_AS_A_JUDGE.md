This document describes the `LLM-a-a-judge` logic, which is implemented in this project.

The all logic is defined in [`groq_judge.py`](../evals/groq_judge.py).


The model used as `LLM-as-a-judge` is **`openai/gpt-oss-120b`**.

## `GroqJudge()` Class.

The `LLM-as-a-judge` is defined as the `GroqJudge` class in the script. This class inherits from  the `DeepEvalBaseLLM` class from `deepeval.models`.

To use the Groq Api LLM, we must inherit from this `deepeval.models` class and overridde its methods.

The attributes are : 

- **model_name : str** : the model name as defined in the Groq API.
- **client : Groq object** :  the client entrypoint to the Groq API.

The methods are:

- **load_model() -> Groq object**: load the model throught the Groq client.
- **generate(prompt : str) -> str** : generate model's anwser from prompt's user.
- **a_generate(prompt : str) -> str** : generate async model's anwser from prompt's user.
- **get_model_name() -> str**: return the model's name.


