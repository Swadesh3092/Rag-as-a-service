import os  # Read configuration from the current process's environment.  # Import Python's built-in hidden-input function.
import requests  # Import the HTTP library we installed.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Read the key from an environment variable.
if not api_key:  # Check whether a key was supplied.
    raise SystemExit("No API key entered.")  # Stop before sending an unauthenticated request.

headers = {"Authorization": f"Bearer {api_key}"}  # Put the key in the authentication header.

try:  # Handle connection and HTTP failures.
    response = requests.get("https://api.agentset.ai/v1/namespace", headers=headers, timeout=30)  # Request the organization's namespaces.
    print(f"HTTP status: {response.status_code}")  # Display the server's response status.
    response.raise_for_status()  # Stop this attempt if the server returned an HTTP error.
    data = response.json()  # Convert the JSON response into Python data.
    namespaces = data["data"]  # Extract the documented list of namespaces.
    print(f"Namespaces found: {len(namespaces)}")  # Show how many namespaces were returned.
    for namespace in namespaces:  # Visit each returned namespace.
        print(f"{namespace['name']} | ID: {namespace['id']}")  # Display its name and identifier.
except requests.exceptions.RequestException as error:  # Catch network, timeout, and HTTP errors.
    print(f"Request failed: {error}")  # Describe the failure without printing the authentication header.
except (ValueError, KeyError, TypeError) as error:  # Catch an unexpected response format.
    print(f"Unexpected response format: {error}")  # Explain that the response could not be read as expected.