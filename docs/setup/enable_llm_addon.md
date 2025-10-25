# Enable LLM Add-on for Real Conversational Search

## Option 1: Via Console (Easiest)

1. Go to [Vertex AI Agent Builder Console](https://console.cloud.google.com/gen-ai/builder/data-stores)
2. Select project: `admin-workstation`
3. Click on datastore: `nq-html-docs-search`
4. Go to **"Configuration"** tab
5. Under **"Advanced features"**, enable:
   - ✅ **"Conversational search"** (LLM add-on)
   - ✅ **"Summarization"**
6. Choose model:
   - **Gemini 1.5 Pro** (best quality, ~1-2s latency)
   - **Gemini 1.5 Flash** (faster, ~0.5-1s latency)
7. Click **"Save"**

## Option 2: Via gcloud CLI

```bash
# Enable conversation feature on the datastore
gcloud alpha discovery-engine data-stores update nq-html-docs-search \
  --location=global \
  --collection=default_collection \
  --project=admin-workstation \
  --solution-types=SOLUTION_TYPE_SEARCH,SOLUTION_TYPE_CHAT \
  --content-config=CONTENT_REQUIRED

# Configure the conversation spec
gcloud alpha discovery-engine data-stores update nq-html-docs-search \
  --location=global \
  --collection=default_collection \
  --project=admin-workstation \
  --conversation-config='{
    "agent_config": {
      "summarization_model_spec": {
        "model_version": "gemini-1.5-flash-001"
      }
    }
  }'
```

## Option 3: Via Python Script

```bash
cd /Users/source-code/vertex-ai-search
python3 enable_llm.py
```

## Cost Implications

- **One-time**: ~$0 (just configuration change)
- **Per 1,000 queries**: ~$2-5 depending on model
- **Monthly with 10K queries**: ~$20-50

## What Changes After Enabling

1. **Conversational Search** API becomes available
2. Can generate natural language answers (not just search results)
3. Includes source citations from your documents
4. Multi-turn conversations supported
5. ~1-3 second response times (depending on model)

## Next Steps

Once enabled (takes ~5 minutes to activate):
1. Run `python3 test_real_conversation.py` to verify it works
2. Run `python3 benchmark_cox_real.py` for actual benchmarks
3. Test both Gemini Pro and Flash to compare performance
