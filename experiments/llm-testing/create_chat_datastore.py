#!/usr/bin/env python3
"""
Create a NEW datastore with BOTH Search and Chat capabilities enabled.
This will allow real conversational AI benchmarking.
"""


from google.cloud import discoveryengine_v1 as discoveryengine

PROJECT_ID = "admin-workstation"
NEW_DATASTORE_ID = "nq-chat-benchmark"
GCS_URI = "gs://nq-html-docs-20251024/html-docs/*"


def create_chat_enabled_datastore() -> None:
    """Create a new datastore with conversational search enabled from the start."""
    print("=" * 70)
    print("🚀 CREATING NEW DATASTORE WITH CHAT CAPABILITIES")
    print("=" * 70)

    client = discoveryengine.DataStoreServiceClient()

    print(f"\n📦 New Datastore ID: {NEW_DATASTORE_ID}")
    print(f"🔧 Project: {PROJECT_ID}")
    print(f"📁 Data source: {GCS_URI}")

    # Create datastore with BOTH search and chat
    data_store = discoveryengine.DataStore(
        display_name="NQ Chat Benchmark - Cox Testing",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        # THIS IS THE KEY - Enable BOTH capabilities
        solution_types=[
            discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
            discoveryengine.SolutionType.SOLUTION_TYPE_CHAT,  # Enables LLM
        ],
    )

    parent = f"projects/{PROJECT_ID}/locations/global/collections/default_collection"

    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=NEW_DATASTORE_ID,
    )

    try:
        print("\n⏳ Creating datastore with chat capabilities...")
        operation = client.create_data_store(request=request)

        print("⏳ Waiting for datastore creation (30-60 seconds)...")
        response = operation.result(timeout=300)

        print(f"✅ Datastore created: {response.name}")
        print(f"   Solution types: {list(response.solution_types)}")

        # Now import the documents
        print("\n📥 Importing documents from GCS...")
        import_documents(response.name)

    except Exception as e:
        if "already exists" in str(e):
            print(f"\n✅ Datastore '{NEW_DATASTORE_ID}' already exists!")
            print("   Proceeding with document import...")

            datastore_path = f"{parent}/dataStores/{NEW_DATASTORE_ID}"
            import_documents(datastore_path)
        else:
            print(f"\n❌ Error: {e}")
            raise


def import_documents(datastore_name: str) -> None:
    """Import documents from GCS into the new datastore."""
    client = discoveryengine.DocumentServiceClient()

    # Configure import
    gcs_source = discoveryengine.GcsSource(
        input_uris=[GCS_URI],
        data_schema="content",  # For unstructured HTML
    )

    import_config = discoveryengine.ImportDocumentsRequest.InlineSource(
        gcs_source=gcs_source
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=f"{datastore_name}/branches/default_branch",
        inline_source=import_config,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    print(f"📤 Starting document import from: {GCS_URI}")
    operation = client.import_documents(request=request)

    print("⏳ Import started. This will take 10-30 minutes...")
    print("\n📊 Import Details:")
    print("   • Source: 1,600 HTML documents")
    print("   • Size: ~368 MB")
    print(f"   • Datastore: {NEW_DATASTORE_ID}")

    print("\n✅ Import operation started successfully!")
    print(f"   Operation name: {operation.name}")

    print("\n⏰ NEXT STEPS:")
    print("   1. Wait 10-30 minutes for import to complete")
    print("   2. The datastore will be ready for REAL conversational benchmarks")
    print("   3. Run: python3 test_real_conversation.py")
    print("   4. Run: python3 benchmark_cox_real.py")
    print("\n   Monitor progress at:")
    print(
        f"   https://console.cloud.google.com/gen-ai/builder/data-stores/{NEW_DATASTORE_ID}"
    )


if __name__ == "__main__":
    create_chat_enabled_datastore()
