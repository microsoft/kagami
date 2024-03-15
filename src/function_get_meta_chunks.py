import azure.durable_functions as df
from langchain_core.documents import Document
from typing import List
import logging, time

import tiktoken

get_meta_chunks_blueprint = df.Blueprint()


@get_meta_chunks_blueprint.activity_trigger(input_name="chunks")
def get_meta_chunks(chunks: List[Document]) -> str:
    cl100k_base = tiktoken.get_encoding("cl100k_base")
    tokens = 0
    for chunk in chunks:
        tokens += len(cl100k_base.encode(chunk))
    start_time = time.time()
    # using the first and last chunks as the intro and conclusion
    # todo: use a more sophisticated method to determine intro and conclusion
    # potentially a summarization of individual chunks and then asking AOAI to choose relevant ones
    # with preference given to the beginning and end of the document
    meta_chunks: List[Document] = []
    meta_chunks.append(chunks[0])
    meta_chunks.append(chunks[-1])
                       
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"get_meta_chunks took {elapsed_time} seconds for {tokens} tokens worth of chunks.")
                       
    return meta_chunks
