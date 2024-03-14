import azure.durable_functions as df
import logging

classify_chunks_blueprint = df.Blueprint()


@classify_chunks_blueprint.activity_trigger(input_name="chunks")
def classify_chunks(chunks: str) -> str:
    logging.info(f"Called classify_chunks on {chunks}!")
    return chunks
