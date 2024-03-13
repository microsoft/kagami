from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# import azure.durable_functions as df
import azure.functions as func
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
import logging
import os
import json
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

app = func.FunctionApp()


@app.blob_trigger(
    arg_name="myblob",
    path="incoming/{name}",
    connection="INCOMING_BLOB_STORAGE_CONNECTION",
)
async def blob_trigger(myblob: func.InputStream) -> None:
    logging.info(
        f"Python blob trigger function processed blob"
        f"Name: {myblob.name}"
        f"Blob Size: {myblob.length} bytes"
    )

    endpoint = os.getenv("AI_MULTISERVICE_ENDPOINT")
    key = os.getenv("AI_MULTISERVICE_KEY")
    script_directory = os.path.dirname(__file__)
    plugins_directory = os.path.join(script_directory, "plugins")

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
        ("####", "Header 4"),
    ]

    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs_string = docs[0].page_content
    splits = text_splitter.split_text(docs_string)

    chunks = []
    for split in splits:
        chunks.append(split.page_content)

    # setup semantic kernel
    aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
    aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    kernel = sk.Kernel()
    service_id = "default"
    service = AzureChatCompletion(
        service_id=service_id,
        deployment_name=aoai_deployment,
        endpoint=aoai_endpoint,
        api_key=aoai_key,
    )
    kernel.add_service(service)

    plugin_names = [
        plugin
        for plugin in os.listdir(plugins_directory)
        if os.path.isdir(os.path.join(plugins_directory, plugin))
    ]

    # for each plugin, add the plugin to the kernel
    try:
        for plugin_name in plugin_names:
            kernel.import_plugin_from_prompt_directory(plugins_directory, plugin_name)
    except ValueError as e:
        logging.exception(f"Plugin {plugin_name} not found")

    # entity extraction
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i}")
        extract_entities_result = await kernel.invoke(
            kernel.plugins["EntityExtraction"]["ExtractMultipleEntities"],
            sk.KernelArguments(input=chunk),
        )
        print(extract_entities_result.value[0].content)
        # todo: test that output is well-formatted json
        # extracted_entities = json.load(extract_entities_result.value[0].content)
        # todo: contstruct final result comparing all chunks results
        extract_stakeholders_result = await kernel.invoke(
            kernel.plugins["EntityExtraction"]["ExtractStakeholders"],
            sk.KernelArguments(input=chunk),
        )
        print(extract_stakeholders_result.value[0].content)
      
        extract_dates_result = await kernel.invoke(
            kernel.plugins["EntityExtraction"]["ExtractSignificantDates"],
            sk.KernelArguments(input=chunk),
        )
        print(extract_dates_result.value[0].content)
        
    print("completed")
    # todo: send final results to dataverse
