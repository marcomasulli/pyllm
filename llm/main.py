import anthropic
import argparse
import sqlite3
import os
from rich.console import Console
from rich.markdown import Markdown
from typing import Iterable, Union, Literal, List, Optional

console = Console()

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.environ.get('ANTHROPIC_API_KEY'),
)

parser = argparse.ArgumentParser(description='Call a remote API and render the response')
parser.add_argument('-m', '--message', type=str, required=True, help='Input messages to send to the API')
parser.add_argument('-model', choices=['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307', 'claude-2.1', 'claude-2.0', 'claude-instant-1.2'], required=False, help='Model to use for the API call')
parser.add_argument('-t', '--max_tokens', type=int, required=False, help='Maximum number of tokens to generate')
parser.add_argument('-metadata', type=str, default=None, help='Metadata to include with the API call')
parser.add_argument('-stop_sequences', nargs='+', default=None, help='List of stop sequences for the API call')
parser.add_argument('-stream', action='store_true', help='Whether to stream the response from the API')
parser.add_argument('-system', type=str, default=None, help='System prompt for the API call')
parser.add_argument('-temperature', type=float, default=None, help='Temperature for the API call')
parser.add_argument('-top_k', type=int, default=None, help='Top-k value for the API call')
parser.add_argument('-top_p', type=float, default=None, help='Top-p value for the API call')
parser.add_argument('-extra_headers', type=str, default=None, help='Extra headers to include with the API call')
parser.add_argument('-extra_query', type=str, default=None, help='Extra query parameters to include with the API call')
parser.add_argument('-extra_body', type=str, default=None, help='Extra body parameters to include with the API call')

args = parser.parse_args()


def call_llm(
    message: str,
    model: Union[str, Literal['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307', 'claude-2.1', 'claude-2.0', 'claude-instant-1.2']] = 'claude-3-sonnet-20240229',
    max_tokens: int = 1000,
    metadata: 'message_create_params.Metadata | NotGiven' = None,
    stop_sequences: 'List[str] | NotGiven' = None,
    stream: 'Literal[False] | Literal[True] | NotGiven' = None,
    system: 'str | NotGiven' = None,
    temperature: 'float | NotGiven' = 0.0,
    top_k: 'int | NotGiven' = None,
    top_p: 'float | NotGiven' = None,
    extra_headers: 'Headers | None' = None,
    extra_query: 'Query | None' = None,
    extra_body: 'Body | None' = None
) -> Optional[str]:
    # Replace with your actual API endpoint and headers
    try:
        
        response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.0,
        system=""" - You are an experienced coder. 
                - Reply with text formatted in markdown.
                - prepend triple double quotes to your output""",
        messages=[
                {"role": "user", "content": message}
            ]
        )

        # message = message.content[0].text.split('"""')[1]
        return response
    except Exception as e:
        console.print_exception(show_locals=True)
        return None

def save_to_db(
    message: str,
    output_text: str = None,
    model: str = None,
    max_tokens: int = None,
    metadata: 'message_create_params.Metadata | NotGiven' = None,
    stop_sequences: 'List[str] | NotGiven' = None,
    stream: 'Literal[False] | Literal[True] | NotGiven' = None,
    system: 'str | NotGiven' = None,
    temperature: 'float | NotGiven' = None,
    top_k: 'int | NotGiven' = None,
    top_p: 'float | NotGiven' = None,
    extra_headers: 'Headers | None' = None,
    extra_query: 'Query | None' = None,
    extra_body: 'Body | None' = None
):
    conn = sqlite3.connect('llm.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (message TEXT, output TEXT, model TEXT, max_tokens INTEGER, metadata TEXT, stop_sequences TEXT, stream BOOLEAN, system TEXT, temperature REAL, top_k INTEGER, top_p REAL, extra_headers TEXT, extra_query TEXT, extra_body TEXT)''')
    c.execute(
        "INSERT INTO history (message, output, model, max_tokens, metadata, stop_sequences, stream, system, temperature, top_k, top_p, extra_headers, extra_query, extra_body) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (str(message), output_text, model, max_tokens, str(metadata), str(stop_sequences), stream, system, temperature, top_k, top_p, str(extra_headers), str(extra_query), str(extra_body))
    )
    conn.commit()
    conn.close()

def main():
    response = call_llm(
        message=args.message,
        model=args.model,
        max_tokens=args.max_tokens,
        metadata=args.metadata,
        stop_sequences=args.stop_sequences,
        stream=args.stream,
        system=args.system,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        extra_headers=args.extra_headers,
        extra_query=args.extra_query,
        extra_body=args.extra_body
    )

    output_text = response.content[0].text.split('"""')[1]

    if output_text:
        console.print(Markdown(output_text))
        save_to_db(
            message=args.message,
            output_text=output_text,
            model=args.model,
            max_tokens=args.max_tokens,
            metadata=args.metadata,
            stop_sequences=args.stop_sequences,
            stream=args.stream,
            system=args.system,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            extra_headers=args.extra_headers,
            extra_query=args.extra_query,
            extra_body=args.extra_body
        )
    else:
        console.print("[red]Error: Failed to call API[/red]")

if __name__ == '__main__':
    main()