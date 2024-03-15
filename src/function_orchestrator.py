import azure.durable_functions as df
import logging

orchestrator_blueprint = df.Blueprint()


@orchestrator_blueprint.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    file_uri: str = context.get_input()

    if context.is_replaying is False:
        logging.info(f"Orchestration {context.instance_id}: Starting for {file_uri}.")

    chunks = yield context.call_activity("chunk_file", file_uri)

    has_handwriting = yield context.call_activity("check_handwriting", file_uri)
  
    meta_chunks = yield context.call_activity("get_meta_chunks", chunks)

    if context.is_replaying is False:
        logging.info(
            f"Orchestration {context.instance_id}: {len(chunks)} chunks found. {len(meta_chunks)} identified."
        )

    tasks = [
        context.call_activity("analyze_sentiment", meta_chunks),
        context.call_activity("detect_language", meta_chunks),
        context.call_activity("classify_chunks", meta_chunks),
    ]
    metadata_analysis_results = yield context.task_all(tasks)

    final_result = {}

    for k, v in metadata_analysis_results:
        final_result[k] = v

    extraction_tasks = []
    for chunk in chunks:
        extraction_tasks.append(context.call_activity("extract_entities", chunk))

    all_extracted_entity_results = yield context.task_all(extraction_tasks)

    if context.is_replaying is False:
        logging.info(
            f"Orchestration {context.instance_id}: entity extraction performed over all chunks."
        )

    final_result["mode_entities"] = yield context.call_activity(
        "find_mode_entities", all_extracted_entity_results
    )

    final_result["has_handwriting"] = has_handwriting
  
    if context.is_replaying is False:
        logging.info(f"Orchestration {context.instance_id}: mode entities calculated.")

    yield context.call_activity("store_results", final_result)

    return final_result
