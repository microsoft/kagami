import azure.durable_functions as df
from langchain_core.documents import Document
from langdetect import detect_langs
from typing import List
import logging, time

import tiktoken

detect_language_blueprint = df.Blueprint()


@detect_language_blueprint.activity_trigger(input_name="chunks")
def detect_language(chunks: List[Document]) -> tuple[str, List[dict]]:
    cl100k_base = tiktoken.get_encoding("cl100k_base")
    tokens = 0
    for chunk in chunks:
        tokens += len(cl100k_base.encode(chunk))
    start_time = time.time()

    # just using the first chunk for now, if there is a strong likelihood that
    # there are multiple languages in the document then you can change to perform over all chunks
    # to increase likelihood of detecting all languages
    languages_result = detect_langs(chunks[0])

    languages: List[dict] = []

    # flattening this into a str that can be concatenated into comma-delimited result for dataverse
    # but you could also drop the probability and enforce a threshold probability for inclusion
    for lang in languages_result:
        languages.append(f"{lang.lang}: {lang.prob}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"detect_language took {elapsed_time} seconds for {tokens} tokens worth of chunks.")

    return ("languages", languages)
