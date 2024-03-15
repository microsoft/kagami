import azure.durable_functions as df
from langchain_core.documents import Document
import json, os, time
from kernel_factory import KernelFactory
import semantic_kernel as sk
from typing import List

import tiktoken

analyze_sentiment_blueprint = df.Blueprint()


@analyze_sentiment_blueprint.activity_trigger(input_name="chunks")
async def analyze_sentiment(chunks: List[Document]) -> tuple[str, dict]:
    cl100k_base = tiktoken.get_encoding("cl100k_base")
    tokens = 0
    for chunk in chunks:
        tokens += len(cl100k_base.encode(chunk))
    start_time = time.time()

    kernel = KernelFactory.create_kernel()

    # for larger documents the chunk size maybe too large for the plugin to handle simultaneously
    joined_chunks = f"{os.linesep}".join(chunks)

    skresult = await kernel.invoke(
        kernel.plugins["SummaryPlugin"]["AreStudyFindingsSignificant"],
        sk.KernelArguments(input=joined_chunks),
    )

    result = skresult.value[0].content

    if result.lower() == "true":
        result = True
    elif result.lower() == "false":
        result = False
    else:
        result = None

    # considering following lines negligible to performance and thus out of scope for measurement
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"analyze_sentiment took {elapsed_time} seconds for {tokens} tokens worth of chunks.")

    # Attempt to parse the JSON string
    try:
        return ("is_conclusive_and_significant", result)
    except json.JSONDecodeError:
        return ("sentiment", None)
