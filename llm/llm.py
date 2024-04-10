import anthropic
from typing import Iterable, Union, Literal, List, Optional
from rich.console import Console

console = Console()

def call_llm(
    client,
    message: str,
    model: Union[
        str,
        Literal[
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        ],
    ] = "claude-3-sonnet-20240229",
    max_tokens: int = 1000,
    history_messages: list = None,
    metadata: "message_create_params.Metadata | NotGiven" = None,
    stop_sequences: "List[str] | NotGiven" = None,
    stream: "Literal[False] | Literal[True] | NotGiven" = None,
    system: "str | NotGiven" = None,
    temperature: "float | NotGiven" = 0.0,
    top_k: "int | NotGiven" = None,
    top_p: "float | NotGiven" = None,
    extra_headers: "Headers | None" = None,
    extra_query: "Query | None" = None,
    extra_body: "Body | None" = None,
) -> Optional[str]:
    # Replace with your actual API endpoint and headers

    try:
        if history_messages is not None:
            messages = history_messages
            messages.append({"role": "user", "content": message})
        else:
            messages = [{"role": "user", "content": message}]
    except Exception as e:
        console.print_exception(show_locals=True)
        messages = [{"role": "user", "content": message}]

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.0,
            system=""" 
                - You are an experienced coder. 
                - you are using the python package "rich" in your output text. make full use of it!
                - Reply with text formatted in markdown.
                - prepend triple double quotes to your output
                """,
            messages=messages,
        )

        return response
    except Exception as e:
        console.print_exception(show_locals=True)
        return None
