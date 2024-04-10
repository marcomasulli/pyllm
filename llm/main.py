import anthropic
import argparse
import datetime as dt
import sqlite3
import os
import traceback

from rich.console import Console
from rich.markdown import Markdown
from typing import Iterable, Union, Literal, List, Optional

import configparser                                                                                                                                                                                                                                               

from .db import create_db, save_input, save_output, get_history
from .llm import call_llm

                                                                                                                                                                                                                                                                         
config = configparser.ConfigParser()                                                                                                                                                                                                                              
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))     

model = config.get('DEFAULT', 'model')
max_tokens = config.get('DEFAULT', 'max_tokens')
temperature = config.get('DEFAULT', 'temperature')
history = config.getboolean('DEFAULT', 'history')
history_entries = config.get('DEFAULT', 'history_entries')

console = Console()

create_db()

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

parser = argparse.ArgumentParser(
    description="Call a remote API and render the response"
)
parser.add_argument(
    "-m", "--message", required=True, help="Input message to send to the API"
)
parser.add_argument(
    "-model",
    choices=[
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2",
    ],
    default=model,
    help="Model to use for the API call",
)
parser.add_argument(
    "-t",
    "--max_tokens",
    type=int,
    default=max_tokens,
    help="Maximum number of tokens to generate",
)
parser.add_argument(
    "-metadata", type=str, default=None, help="Metadata to include with the API call"
)
parser.add_argument(
    "-stop_sequences",
    nargs="+",
    default=None,
    help="List of stop sequences for the API call",
)
parser.add_argument(
    "-stream",
    action="store_true",
    default=False,
    help="Whether to stream the response from the API",
)
parser.add_argument(
    "-system", type=str, default=None, help="System prompt for the API call"
)
parser.add_argument(
    "-temperature", type=float, default=temperature, help="Temperature for the API call"
)
parser.add_argument(
    "-top_k", type=int, default=None, help="Top-k value for the API call"
)
parser.add_argument(
    "-top_p", type=float, default=None, help="Top-p value for the API call"
)
parser.add_argument(
    "-extra_headers",
    type=str,
    default=None,
    help="Extra headers to include with the API call",
)
parser.add_argument(
    "-extra_query",
    type=str,
    default=None,
    help="Extra query parameters to include with the API call",
)
parser.add_argument(
    "-extra_body",
    type=str,
    default=None,
    help="Extra body parameters to include with the API call",
)
parser.add_argument(
    "-i",
    "--history",
    type=bool,
    default=history,
    help="Whether or not to include history in your messages.",
)
parser.add_argument(
    "-e",
    "--history_entries",
    type=int,
    default=history_entries,
    help="The number of messages to include in history retrieval.",
)

args = parser.parse_args()

def main():
    if args.history:
        history_messages = get_history(args.history_entries)
    else:
        history_messages = None

    response = call_llm(
        client,
        message=args.message,
        model=args.model,
        history_messages=history_messages,
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
        extra_body=args.extra_body,
    )

    save_input(
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
        extra_body=args.extra_body,
    )

    try:
        output_text = response.content[0].text.split('"""')[1]
    except Exception as e:
        console.print(e)
        output_text = response.content[0].text

    if output_text:
        console.print(Markdown(output_text))
    else:
        console.print("[red]Error: Failed to call API[/red]")

    try:
        save_output(response.dict())
    except Exception as e:
        console.print(traceback.format_exc())

if __name__ == "__main__":
    main()
