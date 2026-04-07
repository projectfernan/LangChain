import os

# Set dummy credentials BEFORE any app imports so OpenAI clients
# initialize without errors. No real API calls are made in tests.
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-pytest")
os.environ.setdefault("MODEL_NAME", "gpt-3.5-turbo")
os.environ.setdefault("SUMMARIZER_MODEL_NAME", "gpt-3.5-turbo")
os.environ.setdefault("SUMMARY_TOKEN_THRESHOLD", "1000")
