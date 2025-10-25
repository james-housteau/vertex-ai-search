#!/usr/bin/env python3
"""
Import documents to the new chat-enabled datastore.
"""

from google.cloud import discoveryengine_v1 as discoveryengine

PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-chat-benchmark"  # The new chat-enabled datastore
GCS_URI = "gs://nq-html-docs-20251024/html-docs/*"


def import_documents() -> bool:
    """Import documents from GCS into the chat-enabled datastore."""
    print("=" * 70)
    print("📥 IMPORTING DOCUMENTS TO CHAT-ENABLED DATASTORE")
    print("=" * 70)

    client = discoveryengine.DocumentServiceClient()

    # Construct parent path
    parent = (
        f"projects/{PROJECT_ID}/locations/global/collections/default_collection/"
        f"dataStores/{DATASTORE_ID}/branches/default_branch"
    )

    # Configure GCS source
    gcs_source = discoveryengine.GcsSource(
        input_uris=[GCS_URI],
        data_schema="content",  # For unstructured HTML
    )

    # Create import config with correct structure
    import_config = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=gcs_source,  # Direct attribute, not InlineSource
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    try:
        print(f"\n📦 Datastore: {DATASTORE_ID}")
        print(f"📁 Source: {GCS_URI}")
        print("📊 Documents: 1,600 HTML files")

        print("\n⏳ Starting import operation...")
        operation = client.import_documents(request=import_config)

        print("✅ Import started successfully!")
        print(f"   Operation ID: {operation.name}")

        print("\n⏰ IMPORT TIMELINE:")
        print("   • Processing: 10-30 minutes")
        print("   • Indexing: Additional 5-10 minutes")
        print("   • Total: ~20-40 minutes")

        print("\n📊 WHAT'S HAPPENING:")
        print("   1. Documents are being parsed")
        print("   2. Content is being indexed for search")
        print("   3. LLM is being configured for chat")
        print("   4. Embeddings are being generated")

        print("\n✅ ONCE COMPLETE, YOU CAN:")
        print("   1. Test chat: python3 test_real_conversation_new.py")
        print("   2. Run benchmarks: python3 benchmark_cox_real_new.py")

        print("\n🔗 Monitor progress at:")
        print(
            f"   https://console.cloud.google.com/gen-ai/builder/data-stores/{DATASTORE_ID}"
        )

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    import_documents()
