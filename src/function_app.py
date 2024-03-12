import azure.functions as func
import logging
import os
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

app = func.FunctionApp()

@app.blob_trigger(
    arg_name="myblob",
    path="incoming/{name}",
    connection="IncomingBlobStorageConnection",
)
def blob_trigger(myblob: func.InputStream):
    logging.info(
        f"Python blob trigger function processed blob"
        f"Name: {myblob.name}"
        f"Blob Size: {myblob.length} bytes"
    )

    endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")
    key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")

    print("Using endpoint: ", endpoint)
    print("Using key with length: ", len(key) * "*")

    ai_doc_intel_loader = AzureAIDocumentIntelligenceLoader(
        url_path=myblob.uri,
        api_key=key,
        api_endpoint=endpoint,
        api_model="prebuilt-layout",
    )
    docs = ai_doc_intel_loader.load()

    # Split the document into chunks base on markdown headers.
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs_string = docs[0].page_content
    splits = text_splitter.split_text(docs_string)


@app.function_name(name="HttpTrigger1")
@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
    return func.HttpResponse(
        "This HTTP triggered function executed successfully.", status_code=200
    )
