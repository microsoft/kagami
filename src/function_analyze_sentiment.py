import azure.durable_functions as df
import logging

analyze_sentiment_blueprint = df.Blueprint()


@analyze_sentiment_blueprint.activity_trigger(input_name="chunks")
def analyze_sentiment(chunks: str) -> str:
    logging.info(f"Called analyze_sentiment on {chunks}!")
    return chunks
