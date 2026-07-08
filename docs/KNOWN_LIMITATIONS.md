# Known issues / Limitations

## 1 Unbounded chat history growth
`chat_history` grows indefinitely with each user/assitant exchange (see `chatbot.py`.) This means : 
    - Token usage increases linearly with convesation length
    - Risk of exceeding the model's context window on long conversation
    - Increased cost per request over time