import json
import os
import sqlite3
import datetime as dt
from typing import Iterable, Union, Literal, List, Optional

from rich.console import Console

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../llm.db')

def create_db():

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages
                 (interaction TEXT,
                  message TEXT, 
                  output TEXT, 
                  model TEXT, 
                  max_tokens INTEGER, 
                  metadata TEXT, 
                  stop_sequences TEXT, 
                  stream BOOLEAN, 
                  system TEXT, 
                  temperature REAL, 
                  top_k INTEGER, 
                  top_p REAL, 
                  extra_headers TEXT, 
                  extra_query TEXT, 
                  extra_body TEXT, 
                  content TEXT, 
                  id TEXT, 
                  role TEXT, 
                  stop_reason TEXT, 
                  stop_sequence TEXT, 
                  type TEXT, 
                  input_tokens INTEGER, 
                  output_tokens INTEGER, 
                  datadatetime TEXT
                  )
        """
    )
    conn.commit()
    conn.close()


def save_input(
    message: str,
    output_text: str = None,
    model: str = None,
    max_tokens: int = None,
    metadata: "message_create_params.Metadata | NotGiven" = None,
    stop_sequences: "List[str] | NotGiven" = None,
    stream: "Literal[False] | Literal[True] | NotGiven" = None,
    system: "str | NotGiven" = None,
    temperature: "float | NotGiven" = None,
    top_k: "int | NotGiven" = None,
    top_p: "float | NotGiven" = None,
    extra_headers: "Headers | None" = None,
    extra_query: "Query | None" = None,
    extra_body: "Body | None" = None,
    role: str = "user"
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO messages (
            content, 
            output, 
            model, 
            max_tokens, 
            metadata, 
            stop_sequences, 
            stream, 
            system, 
            temperature, 
            top_k, 
            top_p, 
            extra_headers, 
            extra_query, 
            extra_body,
            role, 
            datadatetime
            ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        """,
        (
            str(message),
            output_text,
            model,
            max_tokens,
            str(metadata),
            str(stop_sequences),
            stream,
            system,
            temperature,
            top_k,
            top_p,
            str(extra_headers),
            str(extra_query),
            str(extra_body),
            role,
            str(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        ),
    )
    conn.commit()
    conn.close()


def save_output(output_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    content = str(output_dict.get('content', [])[0]['text'])
    id = output_dict.get('id', '')
    model = output_dict.get('model', '')
    role = output_dict.get('role', '')
    stop_reason = output_dict.get('stop_reason', '')
    stop_sequence = str(output_dict.get('stop_sequence', None))
    type = output_dict.get('type', '')
    input_tokens = output_dict.get('usage', {}).get('input_tokens', 0)
    output_tokens = output_dict.get('usage', {}).get('output_tokens', 0)
    datadatetime = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    # Insert the data into the table
    c.execute(
        """INSERT INTO messages (
            content, 
            id, 
            model, 
            role, 
            stop_reason, 
            stop_sequence, 
            type, 
            input_tokens, 
            output_tokens, 
            datadatetime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            content,
            id,
            model,
            role,
            stop_reason,
            stop_sequence,
            type,
            input_tokens,
            output_tokens,
            datadatetime,
        ),
    )

    conn.commit()
    conn.close()


def get_history(entries:int=10, 
                cutoff:str=None):

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    results = c.execute(f"""
        Select datadatetime,
               role,
               content
        from messages
        where true
        order by datadatetime
        limit {entries}
    """
    ).fetchall()

    history = [{'role':r[1], 'content':r[2]} for r in results]

    return history

