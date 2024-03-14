import azure.durable_functions as df
import logging

detect_language_blueprint = df.Blueprint()


@detect_language_blueprint.activity_trigger(input_name="chunks")
def detect_language(chunks: str) -> str:
    logging.info(f"Called detect_language on {chunks}!")
    return chunks
