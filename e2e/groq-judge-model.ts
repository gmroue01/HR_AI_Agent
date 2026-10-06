import { OpikBaseModel, type OpikMessage } from 'opik';

/**
 * Opik's TS SDK ships providers for OpenAI/Anthropic/Google/Vertex (via the
 * Vercel AI SDK) but has no Groq provider, so this mirrors
 * evals/deepeval/groq_judge.py's GroqJudge(DeepEvalBaseLLM): a minimal
 * OpikBaseModel wrapping Groq's OpenAI-compatible endpoint with plain
 * fetch (Node 18+ has it built in, and the project already avoids adding
 * an HTTP client dependency just for this — see requirements.txt's use of
 * urllib over requests for the same reason).
 *
 * responseFormat (a Zod schema) is deliberately not enforced at the API
 * level — the same tradeoff GroqJudge.generate() makes in Python. Opik's
 * own GEval/judge prompts already instruct the model in plain text to
 * respond with the exact JSON shape they expect, then parse that string on
 * their end; this class just returns the raw text.
 */
export class GroqJudgeModel extends OpikBaseModel {
  constructor(modelName: string = 'openai/gpt-oss-120b') {
    super(modelName);
  }

  async generateProviderResponse(
    messages: OpikMessage[],
    _options?: Record<string, unknown>,
  ): Promise<unknown> {
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) {
      throw new Error('GROQ_API_KEY is not set — GroqJudgeModel cannot call the Groq API');
    }

    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: this.modelName,
        messages: messages.map((m) => ({ role: m.role, content: m.content })),
      }),
    });

    if (!response.ok) {
      throw new Error(`Groq API error ${response.status}: ${await response.text()}`);
    }

    return response.json();
  }

  async generateString(
    input: string,
    _responseFormat?: unknown,
    options?: Record<string, unknown>,
  ): Promise<string> {
    const result = (await this.generateProviderResponse(
      [{ role: 'user', content: input }],
      options,
    )) as { choices: { message: { content: string } }[] };

    // gpt-oss-120b sometimes wraps JSON answers in a ```json fence even when
    // asked not to — strip it so downstream JSON.parse() in Opik doesn't choke.
    return result.choices[0].message.content
      .replace(/^```(?:json)?\s*/i, '')
      .replace(/```\s*$/i, '')
      .trim();
  }
}
