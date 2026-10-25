import os  # Read the key from the current terminal environment.
import requests  # Identify network and HTTP exceptions.
from retrieval import retrieve_chunks  # Import the new reusable search function.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset key without storing it in code.
if not api_key:  # Check that authentication is configured.
    raise SystemExit("Set AGENTSET_API_KEY in this terminal first.")  # Stop if the key is unavailable.

question = "Who was player of the match in the Royal Challengers Bangalore versus Kolkata Knight Riders match on 2008-04-18?"  # Reuse our successful retrieval question.
namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Search the namespace containing matches.csv.

try:  # Let the caller handle failures from the reusable function.
    chunks = retrieve_chunks(question, namespace_id, api_key)  # Run retrieval without calling Groq.
    print(f"Chunks returned: {len(chunks)}")  # Display how many chunks were returned.
    for index, chunk in enumerate(chunks, start=1):  # Inspect each returned passage.
        print(f"\nResult {index}")  # Identify the passage in the output.
        print(chunk.get("text", "[No text returned]"))  # Display the evidence for manual verification.
except requests.exceptions.RequestException as error:  # Catch HTTP, network, and timeout failures.
    print(f"Retrieval request failed: {error}")  # Explain that search failed rather than claiming nothing was found.
except ValueError as error:  # Catch invalid JSON or an unexpected response structure.
    print(f"Retrieval response could not be read: {error}")  # Display the response-processing problem.