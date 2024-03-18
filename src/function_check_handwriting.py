from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import azure.durable_functions as df
import os

import time

check_handwriting_blueprint = df.Blueprint()


@check_handwriting_blueprint.activity_trigger(input_name="fileUri")
def check_handwriting(fileUri: str) -> bool:
    start_time = time.time()
    endpoint = os.getenv("AI_MULTISERVICE_ENDPOINT")
    key = os.getenv("AI_MULTISERVICE_KEY")

    credential = AzureKeyCredential(key)
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=credential)

    poller = client.begin_analyze_document("prebuilt-layout", AnalyzeDocumentRequest(url_source=fileUri))
    result = poller.result()

    # considering following lines negligible to performance and thus out of scope for measurement
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"check_handwriting took {elapsed_time} seconds.")

    if result.styles and any([style.is_handwritten for style in result.styles]):
        return True
    else:
        return False
