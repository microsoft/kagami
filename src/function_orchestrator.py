import azure.durable_functions as df
import logging

orchestrator_blueprint = df.Blueprint()


@orchestrator_blueprint.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    file_uri: str = context.get_input()

    if context.is_replaying is False:
        logging.info(f"Starting orchestrator for {file_uri}...")

    chunks = yield context.call_activity("chunk_file", file_uri)
    # gets intro and conclusion chunks
    meta_chunks = yield context.call_activity("get_meta_chunks", chunks)
    classification_analysis = yield context.call_activity(
        "classify_chunks", meta_chunks
    )
    sentiment_analysis = yield context.call_activity("analyze_sentiment", meta_chunks)
    detected_language = yield context.call_activity("detect_language", meta_chunks)
    extracted_entities = yield context.call_activity("extract_entities", chunks)

    yield context.call_activity(
        "store_results",
        {
            "classification": classification_analysis,
            "sentiment": sentiment_analysis,
            "language": detected_language,
            "entities": extracted_entities,
        },
    )
