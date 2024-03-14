import azure.durable_functions as df
from langchain_core.documents import Document
from typing import List

get_meta_chunks_blueprint = df.Blueprint()


@get_meta_chunks_blueprint.activity_trigger(input_name="chunks")
def get_meta_chunks(chunks: List[Document]) -> str:
    # using the first and last chunks as the intro and conclusion
    # todo: use a more sophisticated method to determine intro and conclusion
    # potentially a summarization of individual chunks and then asking AOAI to choose relevant ones
    # with preference given to the beginning and end of the document
    meta_chunks: List[Document] = []
    meta_chunks.append(chunks[0]).append(chunks[-1])
    return meta_chunks
