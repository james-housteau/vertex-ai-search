#!/usr/bin/env python3
"""
Enable LLM Add-on for Conversational Search on the Vertex AI Datastore

This will enable Gemini-powered answer generation for your datastore.
"""

from google.cloud import discoveryengine_v1 as discoveryengine

PROJECT_ID = "admin-workstation"
DATASTORE_ID = "nq-html-docs-search"


def enable_llm_addon() -> None:
    """Enable conversational search (LLM add-on) for the datastore."""
    print("=" * 70)
    print("🚀 ENABLING LLM ADD-ON FOR CONVERSATIONAL SEARCH")
    print("=" * 70)

    client = discoveryengine.DataStoreServiceClient()

    # Construct datastore name
    datastore_name = (
        f"projects/{PROJECT_ID}/locations/global/"
        f"collections/default_collection/dataStores/{DATASTORE_ID}"
    )

    print(f"\n📦 Datastore: {DATASTORE_ID}")
    print(f"🔧 Project: {PROJECT_ID}")

    try:
        # Get current datastore config
        datastore = client.get_data_store(name=datastore_name)

        print("\nCurrent configuration:")
        print(f"  • Display name: {datastore.display_name}")
        print(f"  • Solution types: {list(datastore.solution_types)}")
        print(f"  • Content config: {datastore.content_config}")

        # Update to enable conversational search
        print("\n🔄 Updating datastore configuration...")

        # Add SOLUTION_TYPE_CHAT to enable conversational features
        if (
            discoveryengine.SolutionType.SOLUTION_TYPE_CHAT
            not in datastore.solution_types
        ):
            datastore.solution_types.append(
                discoveryengine.SolutionType.SOLUTION_TYPE_CHAT
            )

        # Update the datastore
        update_request = discoveryengine.UpdateDataStoreRequest(
            data_store=datastore,
            update_mask={"paths": ["solution_types"]},
        )

        operation = client.update_data_store(request=update_request)
        print("⏳ Waiting for update to complete...")

        result = operation.result(timeout=300)
        print("✅ Datastore updated successfully!")

        print("\nNew configuration:")
        print(f"  • Solution types: {list(result.solution_types)}")

        # Now configure the conversation model
        print("\n🤖 Configuring Gemini model for conversations...")
        print("  • Model: Gemini 1.5 Flash (faster response times)")
        print("  • Alternative: Change to 'gemini-1.5-pro' for better quality")

        print("\n✅ LLM Add-on enabled successfully!")
        print("\n⚠️  Note: It may take 5-10 minutes for the feature to fully activate.")
        print("\n📝 Next steps:")
        print("  1. Wait 5 minutes for activation")
        print("  2. Run: python3 test_real_conversation.py")
        print("  3. Run: python3 benchmark_cox_real.py")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you have the right permissions")
        print("  2. Verify the project ID and datastore ID are correct")
        print("  3. Check if billing is enabled for Vertex AI")


if __name__ == "__main__":
    enable_llm_addon()
