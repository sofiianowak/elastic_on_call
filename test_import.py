import sys
import traceback

print("Testing imports...")
try:
    import elasticsearch
    print("Elasticsearch imported!")
except Exception as e:
    print("Elasticsearch failed!")
    traceback.print_exc()

try:
    from dotenv import load_dotenv
    print("dotenv imported!")
except Exception as e:
    print("dotenv failed!")
    traceback.print_exc()
