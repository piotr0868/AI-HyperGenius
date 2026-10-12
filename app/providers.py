"""SDK ufficiali e protocollo persistente comune: nessun provider simulato in produzione."""
from dataclasses import dataclass
import groq
import openai


@dataclass
class Reply:
    id: str
    output: list[dict]
    output_text: str
    input_tokens: int | None
    output_tokens: int | None


class ProviderError(RuntimeError):
    def __init__(self, status=None, retry_after=None):
        self.status = status
        self.retry_after = retry_after
        super().__init__('Errore del provider IA')


def create_client(settings, timeout=45):
    if settings.provider == 'groq':
        return groq.AsyncGroq(api_key=settings.api_key, base_url='https://api.groq.com',
                              timeout=timeout, max_retries=0)
    if settings.provider == 'openai':
        return openai.AsyncOpenAI(api_key=settings.api_key, base_url='https://api.openai.com/v1',
                                  timeout=timeout, max_retries=0)
    raise ValueError('Provider non supportato')


def chat_messages(history, instructions):
    """Converte anche cronologie Responses preesistenti senza perdere chiamate e risultati."""
    messages = [{'role': 'system', 'content': instructions}]
    pending = []
    def flush():
        if pending:
            messages.append({'role': 'assistant', 'content': None, 'tool_calls': list(pending)})
            pending.clear()
    for item in history:
        kind = item.get('type')
        if kind == 'function_call':
            pending.append({'id': item['call_id'], 'type': 'function',
                            'function': {'name': item['name'], 'arguments': item['arguments']}})
            continue
        flush()
        if kind == 'function_call_output':
            messages.append({'role': 'tool', 'tool_call_id': item['call_id'], 'content': item['output']})
        elif kind == 'message':
            content = ''.join(p.get('text', '') for p in item.get('content', []) if isinstance(p, dict))
            if content:
                messages.append({'role': item.get('role', 'assistant'), 'content': content})
        elif kind is None and item.get('role') in ('user', 'assistant', 'system'):
            messages.append({'role': item['role'], 'content': item['content']})
        # I blocchi reasoning specifici di Responses non sono messaggi Chat Completions.
    flush()
    return messages


async def generate(settings, client, history, instructions, tools=None, max_output=None):
    maximum = max_output or settings.max_output_tokens
    try:
        if settings.provider == 'openai':
            kwargs = dict(model=settings.model, instructions=instructions, input=history,
                          max_output_tokens=maximum, store=False)
            if tools:
                kwargs.update(tools=tools, parallel_tool_calls=False)
            response = await client.responses.create(**kwargs)
            return Reply(response.id,
                         [item.model_dump(mode='json', by_alias=True, exclude_none=True) for item in response.output],
                         response.output_text,
                         response.usage.input_tokens if response.usage else None,
                         response.usage.output_tokens if response.usage else None)
        if settings.provider != 'groq':
            raise ValueError('Provider non supportato')
        kwargs = dict(model=settings.model, messages=chat_messages(history, instructions),
                      max_completion_tokens=maximum)
        if tools:
            kwargs.update(tools=[{'type': 'function', 'function': {k: t[k] for k in ('name', 'description', 'parameters')}} for t in tools],
                          parallel_tool_calls=False, tool_choice='auto')
        response = await client.chat.completions.create(**kwargs)
        if not response.choices:
            raise ProviderError(status=502)
        message = response.choices[0].message
        output = []
        if message.content:
            output.append({'type': 'message', 'role': 'assistant',
                           'content': [{'type': 'output_text', 'text': message.content, 'annotations': []}]})
        for call in message.tool_calls or []:
            output.append({'type': 'function_call', 'call_id': call.id,
                           'name': call.function.name, 'arguments': call.function.arguments})
        return Reply(response.id, output, message.content or '',
                     response.usage.prompt_tokens if response.usage else None,
                     response.usage.completion_tokens if response.usage else None)
    except (groq.APIStatusError, openai.APIStatusError) as exc:
        raw = exc.response.headers.get('retry-after', '')
        retry = int(raw) if raw.isdigit() and int(raw) <= 86400 else None
        raise ProviderError(exc.status_code, retry) from None
    except (groq.APIConnectionError, openai.APIConnectionError):
        raise ProviderError() from None
