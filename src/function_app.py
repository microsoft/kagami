
import azure.functions as func
import azure.durable_functions as df
import logging

from function_orchestrator import orchestrator_blueprint
from function_chunk_file import chunk_file_blueprint
from function_get_meta_chunks import get_meta_chunks_blueprint
from function_classify_chunks import classify_chunks_blueprint
from function_analyze_sentiment import analyze_sentiment_blueprint
from function_detect_language import detect_language_blueprint
from function_extract_entities import extract_entities_blueprint
from function_find_mode_entities import find_mode_entities_blueprint

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(orchestrator_blueprint)
app.register_functions(chunk_file_blueprint)
app.register_functions(get_meta_chunks_blueprint)
app.register_functions(classify_chunks_blueprint)
app.register_functions(analyze_sentiment_blueprint)
app.register_functions(detect_language_blueprint)
app.register_functions(find_mode_entities_blueprint)
app.register_functions(extract_entities_blueprint)


@app.blob_trigger(
    arg_name="myblob",
    path="incoming/{name}",
    connection="INCOMING_BLOB_STORAGE_CONNECTION",
)
@app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client) -> None:
    instance_id = await client.start_new("orchestrator", None, myblob.uri)
    logging.info(f"Orchcestration started for {myblob.name} with ID = '{instance_id}'.")