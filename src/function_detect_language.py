import azure.durable_functions as df
from langchain_core.documents import Document
from langdetect import detect_langs
from typing import List

detect_language_blueprint = df.Blueprint()


@detect_language_blueprint.activity_trigger(input_name="chunks")
def detect_language(chunks: List[Document]) -> tuple[str, List[dict]]:
    # just using the first chunk for now, if there is a strong likelihood that
    # there are multiple languages in the document then you can change to perform over all chunks
    # to increase likelihood of detecting all languages
    languages_result = detect_langs(chunks[0])

    languages: List[dict] = []

    for lang in languages_result:
        languages.append({"language": lang.lang, "probability": lang.prob})

    return ("languages", languages)
