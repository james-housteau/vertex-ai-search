#!/usr/bin/env python3
"""Check import operation status."""

from google.cloud import discoveryengine_v1 as discoveryengine

OPERATION_ID = "projects/546806894637/locations/global/collections/default_collection/dataStores/nq-html-docs-search/branches/0/operations/import-documents-10588531613914936830"


def check_status() -> None:
    """Check import status."""
    client = discoveryengine.DataStoreServiceClient()

    try:
        # Get operation status
        operation = client.get_operation(request={"name": OPERATION_ID})

        print("📊 Import Operation Status")
        print("=" * 50)
        print(f"Operation ID: {operation.name}")
        print(f"Done: {operation.done}")

        if operation.done:
            if operation.error and operation.error.message:
                print(f"❌ Error: {operation.error.message}")
            else:
                print("✅ Import completed successfully!")
                print("\n🎉 Your datastore is ready for search queries!")
        else:
            print("⏳ Still importing... (this takes 10-30 minutes)")

        print("=" * 50)

    except Exception as e:
        print(f"Error checking status: {e}")


if __name__ == "__main__":
    check_status()
