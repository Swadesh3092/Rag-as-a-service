import os  # Read the API key from the terminal environment.
import requests  # Identify HTTP and network failures.
from ingestion import create_ingest_job  # Import our document submission function.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset credential.
if not api_key:  # Check that authentication is configured.
    raise SystemExit("Set AGENTSET_API_KEY in this terminal first.")  # Stop when the credential is missing.

namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Use our existing namespace.
document_url = input("Paste a public document URL: ").strip()  # Collect the document URL without editing the script.

try:  # Let this test script display results and failures.
    job = create_ingest_job(document_url, namespace_id, api_key)  # Submit the document once.
    print("Job ID:", job["id"])  # Display the identifier needed for our next step.
    print("Status:", job["status"])  # Display the status returned during creation.
    print("Keep this job ID for the processing-status check.")  # Explain what we need next.
except requests.exceptions.RequestException as error:  # Catch rejected requests, timeouts, and connection failures.
    print("Ingestion request failed:", error)  # Explain that submission could not be confirmed.
except ValueError as error:  # Catch invalid URLs, invalid JSON, or unexpected response data.
    print("Ingestion could not be processed:", error)  # Display the validation problem.