"""SDK ufficiali e protocollo persistente comune: nessun provider simulato in produzione."""
from dataclasses import dataclass
import copy
import json
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
    def __init__(self, status=None, retry_after=None, quota=None, diagnostic=None):
        self.status = status
        self.retry_after = retry_after
        self.quota = quota or {}
        self.diagnostic = diagnostic or {}
        super().__init__('Errore del provider IA')


def request_diagnostic(body):
    """Classifica il rifiuto senza conservare messaggi, prompt o generazioni del server."""
    if not isinstance(body, dict):
        return {'category': 'bad_request'}
    error = body.get('error', body)
    if not isinstance(error, dict):
        return {'category': 'bad_request'}
    code = error.get('code')
    message = error.get('message')
    message = message[:4000].lower() if isinstance(message, str) else ''
    category = 'bad_request'
    if code == 'tool_use_failed' or ('failed_generation' in error and
            ('tool call' in message or 'call a function' in message)):
        category = 'invalid_tool_call'
    elif code == 'context_length_exceeded' or 'context length' in message:
        category = 'context_too_large'
    elif 'tool_call_id' in message or ('messages' in message and 'tool' in message):
        category = 'invalid_history'
    elif code == 'unsupported_parameter' or 'parameter' in message:
        category = 'invalid_parameter'
    diagnostic = {'category': category}
    if code in ('tool_use_failed', 'invalid_request_error', 'context_length_exceeded',
                'json_validate_failed', 'unsupported_parameter'):
        diagnostic['code'] = code
    parameter = error.get('param')
    if parameter in ('messages', 'tools', 'tool_choice', 'parallel_tool_calls',
                     'max_completion_tokens', 'max_output_tokens', 'reasoning_effort',
                     'temperature', 'response_format', 'model'):
        diagnostic['parameter'] = parameter
    return diagnostic


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


def groq_messages(history, instructions):
    """Riduce duplicati solo nella richiesta; la memoria originale resta intatta."""
    messages = copy.deepcopy(chat_messages(history, instructions))
    completed = set()
    for message in messages:
        if message['role'] == 'tool':
            try:
                result = json.loads(message['content'])
                if isinstance(result, dict) and 'previous_version' in result and 'path' in result and 'error' not in result:
                    completed.add(message.get('tool_call_id'))
            except (ValueError, TypeError):
                pass
    names = {}
    for message in messages:
        for call in message.get('tool_calls', []):
            function = call['function']
            names[call['id']] = function['name']
            if function['name'] == 'write_file' and call['id'] in completed:
                try:
                    args = json.loads(function['arguments'])
                    if isinstance(args, dict) and isinstance(args.get('content'), str):
                        args['content'] = '[Contenuto della scrittura riuscita non ripetuto. Usa read_file per controllare il file corrente.]'
                        function['arguments'] = json.dumps(args, ensure_ascii=False)
                except (ValueError, TypeError):
                    pass
    for message in messages:
        if message['role'] != 'tool':
            continue
        name = names.get(message.get('tool_call_id'))
        try:
            result = json.loads(message['content'])
        except (ValueError, TypeError):
            continue
        if not isinstance(result, dict):
            continue
        changed = False
        if name == 'fetch_documentation' and isinstance(result.get('content'), str):
            changed = len(result['content']) > 2000
            result['content'] = result['content'][:2000]
        if name == 'search_knowledge':
            for document in result.get('untrusted_references', []):
                if isinstance(document, dict) and isinstance(document.get('content'), str):
                    changed = changed or len(document['content']) > 1200
                    document['content'] = document['content'][:1200]
        if name == 'run_checks':
            for key in ('stdout', 'stderr'):
                if isinstance(result.get(key), str) and len(result[key]) > 1800:
                    result[key] = result[key][-1800:]
                    changed = True
        if changed:
            result['request_excerpt_limited'] = True
            message['content'] = json.dumps(result, ensure_ascii=False)
    return messages


async def generate(settings, client, history, instructions, tools=None, max_output=None, temperature=None):
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
        kwargs = dict(model=settings.model, messages=groq_messages(history, instructions),
                      max_completion_tokens=maximum)
        if settings.model in ('openai/gpt-oss-20b', 'openai/gpt-oss-120b'):
            kwargs['reasoning_effort'] = 'low'
        if tools:
            kwargs.update(tools=[{'type': 'function', 'function': {k: t[k] for k in ('name', 'description', 'parameters')}} for t in tools],
                          parallel_tool_calls=False, tool_choice='auto',
                          temperature=0.4 if temperature is None else temperature)
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
        quota = {}
        if exc.status_code == 429:
            import re
            for key in ('limit-requests', 'remaining-requests', 'reset-requests',
                        'limit-tokens', 'remaining-tokens', 'reset-tokens'):
                value = exc.response.headers.get('x-ratelimit-' + key, '')
                if re.fullmatch(r'[0-9.dhms]{1,48}', value):
                    quota[key] = value
        diagnostic = request_diagnostic(exc.body) if exc.status_code == 400 else {}
        raise ProviderError(exc.status_code, retry, quota, diagnostic) from None
    except (groq.APIConnectionError, openai.APIConnectionError):
        raise ProviderError() from None
