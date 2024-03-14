import azure.durable_functions as df
import logging

get_meta_chunks_blueprint = df.Blueprint()


@get_meta_chunks_blueprint.activity_trigger(input_name="chunks")
def get_meta_chunks(chunks: str) -> str:
    logging.info(f"Called get_meta_chunks")
    return chunks
