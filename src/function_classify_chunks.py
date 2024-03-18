import azure.durable_functions as df
from langchain_core.documents import Document
import json, os, time
from kernel_factory import KernelFactory
import semantic_kernel as sk
from typing import List

import tiktoken

classify_chunks_blueprint = df.Blueprint()


@classify_chunks_blueprint.activity_trigger(input_name="chunks")
async def classify_chunks(chunks: List[Document]) -> tuple[str, dict]:
    cl100k_base = tiktoken.get_encoding("cl100k_base")
    tokens = 0
    for chunk in chunks:
        tokens += len(cl100k_base.encode(chunk))
    start_time = time.time()

    kernel = KernelFactory.create_kernel()

    # for larger documents the chunk size maybe too large for the plugin to handle simultaneously
    joined_chunks = f"{os.linesep}".join(chunks)

    skresult = await kernel.invoke(
        kernel.plugins["ClassificationPlugin"]["ClassifyStudyType"],
        sk.KernelArguments(input=joined_chunks),
    )

    # considering following lines negligible to performance and thus out of scope for measurement
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"classify_chunks took {elapsed_time} seconds for {tokens} tokens worth of chunks.")

    # Attempt to parse the JSON string, recently got back single-quotes around property values so this prompt needs work to avoid json errors
    try:
        return ("classification", json.loads(skresult.value[0].content))
    except json.JSONDecodeError:
        return ("classification", None)
