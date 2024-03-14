import azure.durable_functions as df
import logging

extract_entities_blueprint = df.Blueprint()


@extract_entities_blueprint.activity_trigger(input_name="chunks")
def extract_entities(chunks: str) -> str:
    logging.info(f"Called extract_entities_blueprint on {chunks}!")
    return chunks
