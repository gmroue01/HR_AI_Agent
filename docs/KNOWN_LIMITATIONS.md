### 1. Unbounded chat history growth

`chat_history` grows indefinitely with each user/assistant exchange (see `chatbot.py`).

**Impact:**
- Token usage increases linearly with conversation length
- Risk of exceeding the model's context window on long conversations
- Increased cost per request over time

**Status:** Not addressed — acceptable for prototype/demo use. 
**Possible mitigation:** sliding window (keep last N messages) or summarization of older turns before re-injection.