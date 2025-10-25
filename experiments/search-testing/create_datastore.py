#!/usr/bin/env python3
"""Create a real Vertex AI datastore."""

from google.cloud import discoveryengine_v1 as discoveryengine

# Configuration
PROJECT_ID = "admin-workstation"
LOCATION = "global"
COLLECTION = "default_collection"
DATA_STORE_ID = "nq-html-docs-search"
DISPLAY_NAME = "NQ HTML Documents Search"
GCS_URI = "gs://nq-html-docs-20251024/html-docs/*"


def create_datastore() -> str | None:
    """Create Vertex AI datastore."""

    # Initialize client
    client = discoveryengine.DataStoreServiceClient()

    # Prepare datastore
    data_store = discoveryengine.DataStore(
        display_name=DISPLAY_NAME,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
    )

    # Create request
    request = discoveryengine.CreateDataStoreRequest(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}",
        data_store=data_store,
        data_store_id=DATA_STORE_ID,
    )

    try:
        # Create datastore
        print(f"Creating datastore: {DATA_STORE_ID}...")
        operation = client.create_data_store(request=request)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=300)

        print("\n✅ Datastore created successfully!")
        print(f"   Name: {response.name}")
        print(f"   Display Name: {response.display_name}")

        # Now import documents
        print(f"\n📥 Importing documents from {GCS_URI}...")
        import_documents(response.name)

        return str(response.name)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def import_documents(data_store_name: str) -> None:
    """Import documents into the datastore."""

    client = discoveryengine.DocumentServiceClient()

    # Configure import
    gcs_source = discoveryengine.GcsSource(
        input_uris=[GCS_URI], data_schema="content"  # Unstructured content
    )

    import_config = (
        discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=f"{data_store_name}/branches/default_branch",
        gcs_source=gcs_source,
        reconciliation_mode=import_config,
    )

    try:
        operation = client.import_documents(request=request)
        print(f"Import operation started: {operation.operation.name}")
        print("This will take 10-30 minutes to complete...")
        print("\n💡 You can check status with:")
        print(f"   Operation ID: {operation.operation.name}")

    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_datastore()
