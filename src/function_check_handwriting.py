from azure.ai.documentintelligence import AnalyzeDocumentRequest, DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import azure.durable_functions as df
import os

check_handwriting_blueprint = df.Blueprint()


@check_handwriting_blueprint.activity_trigger(input_name="fileUri")
def check_handwriting(fileUri: str) -> bool:
    endpoint = os.getenv("AI_MULTISERVICE_ENDPOINT")
    key = os.getenv("AI_MULTISERVICE_KEY")

    credential = AzureKeyCredential(key)
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=credential)

    analyze_document_request = AnalyzeDocumentRequest(url_source=fileUri)

    poller = client.begin_analyze_document(
        "prebuilt-layout",
        analyze_document_request=analyze_document_request,
        content_type="application/octet-stream",
    )
    result = poller.result()

    if result.styles and any([style.is_handwritten for style in result.styles]):
        return True
    else:
        return False
