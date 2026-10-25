import os  # Read credentials from the terminal environment.
import requests  # Identify HTTP and network failures.
from ingestion import get_ingest_job  # Import the new status-checking function.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset credential.
if not api_key:  # Check whether authentication is configured.
    raise SystemExit("Set AGENTSET_API_KEY in this terminal first.")  # Stop if the key is missing.

namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Use the namespace containing your job.
job_id = "job_cmvo3cerr000004i60k8mjodg"  # Select your existing Kaggle URL submission.

try:  # Let the test display the returned details or failure.
    job = get_ingest_job(job_id, namespace_id, api_key)  # Check the existing job once.
    print("Job ID:", job["id"])  # Confirm which job was checked.
    print("Status:", job["status"])  # Show the current processing status.
    print("Error:", job.get("error") or "None reported")  # Show any processing error.
    print("Submitted payload:", job.get("payload"))  # Show the document URL associated with this failed job.
    print("Job config:", job.get("config"))  # Show the processing settings used by the successful job.   
    print("Completed at:", job.get("completedAt") or "Not reported")  # Show whether a completion timestamp exists.
except requests.exceptions.RequestException as error:  # Catch HTTP, network, and timeout failures.
    print("Status request failed:", error)  # Distinguish a failed check from a failed ingestion job.
except ValueError as error:  # Catch invalid JSON or unexpected response data.
    print("Status response could not be processed:", error)  # Explain the response problem.