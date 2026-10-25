import os  # Read the credential from the terminal environment.
import requests  # Identify network and HTTP failures.
from retrieval import retrieve_chunks  # Import our updated search function.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset key.
if not api_key:  # Check authentication before searching.
    raise SystemExit("Set AGENTSET_API_KEY in this terminal first.")  # Stop when the key is missing.

namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Select our existing namespace.
document_ids = ["doc_lvghrqg8o0gri2vx9afnmh5o"]  # Select only the verified dummy PDF.

try:  # Display retrieval results or failures.
    chunks = retrieve_chunks("Dummy PDF file", namespace_id, api_key, document_ids=document_ids)  # Search only the selected PDF.
    for chunk in chunks:  # Inspect each returned passage.
        print("Metadata:", chunk.get("metadata"))  # Show the source fields exactly as Agentset returns them.
        print("Document ID:", chunk["metadata"]["documentId"])  # Confirm the passage's document association.
        print("Text:", chunk.get("text"))  # Display the actual retrieved evidence.
except requests.exceptions.RequestException as error:  # Catch HTTP, network, and timeout failures.
    print("Search request failed:", error)  # Explain that retrieval could not complete.
except ValueError as error:  # Catch invalid responses or document ownership failures.
    print("Retrieval validation failed:", error)  # Display the reason retrieval was blocked.