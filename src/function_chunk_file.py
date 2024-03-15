import azure.durable_functions as df
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
import os
from typing import List

chunk_file_blueprint = df.Blueprint()


@chunk_file_blueprint.activity_trigger(input_name="fileUri")
def chunk_file(fileUri: str) -> List[Document]:
    endpoint = os.getenv("AI_MULTISERVICE_ENDPOINT")
    key = os.getenv("AI_MULTISERVICE_KEY")
    ai_doc_intel_loader = AzureAIDocumentIntelligenceLoader(
        url_path=fileUri,
        api_key=key,
        api_endpoint=endpoint,
        api_model="prebuilt-layout",
    )

    docs = ai_doc_intel_loader.load()

    # Split the document into chunks based on markdown headers.
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]

    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    docs_string = docs[0].page_content

    splits = text_splitter.split_text(docs_string)

    chunks: List[Document] = []

    for split in splits:
        chunks.append(split.page_content)

    return chunks
