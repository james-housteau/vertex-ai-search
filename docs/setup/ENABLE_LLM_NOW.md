# ⚠️ CRITICAL: Enable LLM Add-on for Real Benchmarks

The LLM add-on is a **paid feature** that must be explicitly enabled. Creating a datastore with SOLUTION_TYPE_CHAT doesn't automatically enable it.

## Enable It NOW (2 minutes):

### Go to Console:
https://console.cloud.google.com/gen-ai/builder/data-stores/nq-chat-benchmark/apps

### Steps:
1. You should see the `nq-chat-benchmark` datastore
2. Click **"Create App"** button
3. Select **"Chat"** as app type
4. Name: `cox-benchmark-chat`
5. **IMPORTANT**: In "Configurations" section:
   - Enable: **"Enterprise edition features"**
   - Model: **"Gemini 1.5 Flash"** (for speed)
   - Or: **"Gemini 1.5 Pro"** (for quality)
6. Click **"Create"**

## What This Enables:
- ✅ Real LLM-powered answers (not just search)
- ✅ Actual Gemini response times
- ✅ True end-to-end latency measurements
- ✅ Exact reproduction of Cox's Oliver setup

## Cost:
- ~$0.00125 per query (Gemini Flash)
- ~$0.0025 per query (Gemini Pro)
- For 1,000 test queries: ~$1.25-$2.50

## Alternative: Use Cox's Project

If Capgemini has a test project with LLM already enabled:
1. Export the 1,600 HTML docs
2. Import to your existing LLM-enabled datastore
3. Run benchmarks there

## Why This Matters:

Without the LLM add-on, you CANNOT:
- Measure real conversational AI performance
- Compare Gemini Pro vs Flash
- Reproduce Cox's 2.5-second issue
- Provide data-driven optimization recommendations

WITH the LLM add-on, you CAN:
- Get exact millisecond breakdowns
- Test different model configurations
- Prove where Cox's bottleneck is
- Justify optimization strategies with real data
