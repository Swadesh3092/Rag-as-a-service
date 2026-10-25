import os  # Read the API key from the terminal environment.
import requests  # Send the search request to Agentset.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the API key without putting it in this file.
if not api_key:  # Check that the key is available.
    raise SystemExit("Set AGENTSET_API_KEY in this terminal before running the test.")  # Stop if authentication is missing.

namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Select the collection containing your CSV.
url = f"https://api.agentset.ai/v1/namespace/{namespace_id}/search"  # Build the documented search endpoint.
headers = {"Authorization": f"Bearer {api_key}"}  # Authenticate the request with your API key.
payload = {"query": "Who was player of the match in the Royal Challengers Bangalore versus Kolkata Knight Riders match on 2008-04-18?", "topK": 5}  # Find evidence for the player-of-the-match award in this specific game.

try:  # Handle failures while requesting and reading search results.
    response = requests.post(url, headers=headers, json=payload, timeout=30)  # Send the question as JSON to Agentset.
    print(f"HTTP status: {response.status_code}")  # Show whether the server accepted the request.
    response.raise_for_status()  # Stop normal processing if an HTTP error occurred.
    results = response.json()["data"]  # Extract the retrieved chunks from the response.
    print(f"Chunks returned: {len(results)}")  # Show how many chunks were retrieved.
    for index, chunk in enumerate(results, start=1):  # Visit each result in its returned order.
        print(f"\nResult {index} | Score: {chunk['score']}")  # Display the result number and ranking score.
        print(chunk.get("text", "[No text returned]"))  # Display the retrieved passage without truncating it.
        print("Metadata:", chunk.get("metadata", {}))  # Display any source information returned with the chunk.
except requests.exceptions.RequestException as error:  # Catch network, timeout, and HTTP errors.
    print(f"Search request failed: {error}")  # Report the failure without printing the API key.
except (ValueError, KeyError, TypeError) as error:  # Catch an unexpected response format.
    print(f"Unexpected response format: {error}")  # Explain why the returned data could not be processed.