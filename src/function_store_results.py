import azure.durable_functions as df
import os
from azure.storage.blob import BlobServiceClient
import datetime

store_results_blueprint = df.Blueprint()


@store_results_blueprint.activity_trigger(input_name="orchestrationResults")
async def store_results(orchestrationResults) -> None:
    try:
        # Create a blob client using the local file name as the name for the blob
        conn_str = os.getenv("INCOMING_BLOB_STORAGE_CONNECTION")

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        blob_client = blob_service_client.get_blob_client(
            "outputs", f"extracted_content_{timestamp}.json"
        )

        print("\nUploading to Azure Storage as blob:\n\t" + "extracted_content.json")

        # Upload the created file
        blob_client.upload_blob(orchestrationResults, overwrite=True)
    except Exception as ex:
        print("Exception:")
        print(ex)
