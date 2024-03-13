from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# import azure.durable_functions as df
import azure.functions as func
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langdetect import detect_langs
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

    # todo: identify intro and conclusion sections for sentiment analysis, language detection, and and classification
    # for now, just use the first and last chunks
    intro_chunk = chunks[0]
    conclusion_chunk = chunks[-1]

    # study type classification
    intro_classify_study_type_result = await kernel.invoke(
        kernel.plugins["ClassificationPlugin"]["ClassifyStudyType"],
        sk.KernelArguments(input=intro_chunk),
    )
    success, intro_study_type_classification = validate_and_format_json(
        intro_classify_study_type_result.value[0].content, None
    )
    if success is False:
        print(
            "Intro study type classification result is poorly formatted json: ",
            intro_classify_study_type_result.value[0].content,
        )
    conclusion_classify_study_type_result = await kernel.invoke(
        kernel.plugins["ClassificationPlugin"]["ClassifyStudyType"],
        sk.KernelArguments(input=conclusion_chunk),
    )
    success, conclusion_study_type_classification = validate_and_format_json(
        conclusion_classify_study_type_result.value[0].content, None
    )
    if success is False:
        print(
            "Conclusion study type classification result is poorly formatted json: ",
            conclusion_classify_study_type_result.value[0].content,
        )

    # intro & conclusion sentiment analysis
    intro_sentiment_analysis_result = await kernel.invoke(
        kernel.plugins["SummaryPlugin"]["AreStudyFindingsSignificant"],
        sk.KernelArguments(input=intro_chunk),
    )
    intro_shows_conclusive_significant_findings = parse_text_to_boolean(
        intro_sentiment_analysis_result.value[0].content
    )
    if intro_shows_conclusive_significant_findings is None:
        print(
            "Intro sentiment analysis is invalid boolean representation",
            intro_sentiment_analysis_result.value[0].content,
        )
    conclusion_sentiment_analysis_result = await kernel.invoke(
        kernel.plugins["SummaryPlugin"]["AreStudyFindingsSignificant"],
        sk.KernelArguments(input=conclusion_chunk),
    )
    conclusion_shows_conclusive_significant_findings = parse_text_to_boolean(
        intro_sentiment_analysis_result.value[0].content
    )
    if intro_shows_conclusive_significant_findings is None:
        print(
            "Intro sentiment analysis is invalid boolean representation",
            conclusion_sentiment_analysis_result.value[0].content,
        )

    # language detection
    first_chunk_lang = detect_langs(intro_chunk)
    print(first_chunk_lang)

    # entity extraction
    extracted_entity_responses = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i}")
        extract_entities_result = await kernel.invoke(
            kernel.plugins["EntityExtraction"]["ExtractMultipleEntities"],
            sk.KernelArguments(input=chunk),
        )
        success, extracted_entities = validate_and_format_json(
            extract_entities_result.value[0].content, None
        )
        if success is True:
            extracted_entity_responses.append(extracted_entities)
        else:
            print(
                f"Extracted entities result for chunk {i} is poorly formatted json: ",
                extract_entities_result.value[0].content,
            )
    avg_extracted_entities_response = calculate_average_response(
        extracted_entity_responses
    )

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

    success, extracted_entities = validate_and_format_json(
        extract_entities_result.value[0].content, None
    )
    if success:
        print(extracted_entities)

    full_document_analysis_result = {}
    full_document_analysis_result["intro_study_type_classification"] = (
        intro_study_type_classification
    )
    full_document_analysis_result["conclusion_study_type_classification"] = (
        conclusion_study_type_classification
    )
    full_document_analysis_result["intro_shows_conclusive_significant_findings"] = (
        intro_shows_conclusive_significant_findings
    )
    full_document_analysis_result[
        "conclusion_shows_conclusive_significant_findings"
    ] = conclusion_shows_conclusive_significant_findings
    full_document_analysis_result["detected_language_result"] = first_chunk_lang
    full_document_analysis_result["extracted_entities"] = (
        avg_extracted_entities_response
    )

    print(full_document_analysis_result)
    # todo: send final results to dataverse


def validate_and_format_json(json_string, indent=4):
    try:
        # Attempt to parse the JSON string
        parsed_json = json.loads(json_string)
        # If successful, re-encode it with indentation for pretty printing
        return True, json.dumps(parsed_json, indent=indent)
    except json.JSONDecodeError:
        # If parsing fails, return an error message
        return False, None


def parse_text_to_boolean(text):
    if text.lower() == "true":
        return True
    elif text.lower() == "false":
        return False
    else:
        return None


# for simplicity assumes all objects use the same schema
# probably a more performant way to do this
def calculate_average_response(list_of_json_objects):
    first_entry = json.loads(list_of_json_objects[0])

    property_keys = first_entry.keys()

    average_response = {}
    responses = {}
    for key in property_keys:
        for obj in list_of_json_objects:
            json_obj = json.loads(obj)
            value = json_obj[key]
            # todo: determine how to handle list values, for now skipping to prepare for demo
            if isinstance(value, list):
                continue
            if json_obj[key] in responses:
                responses[value] += 1
            else:
                responses[value] = 1
        if len(responses) > 0:
            average_response[key] = max(responses, key=responses.get)
        responses = {}
    return average_response
