import azure.durable_functions as df
import logging

chunker_blueprint = df.Blueprint()


@chunker_blueprint.activity_trigger(input_name="fileUri")
def chunk_file(fileUri: str) -> str:
    logging.info(f"Called chunker on {fileUri}!")
    return fileUri
