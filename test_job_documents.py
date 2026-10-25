import os  # Read credentials from the terminal environment.
import requests  # Identify HTTP and network failures.
from ingestion import get_job_documents  # Import our document lookup function.
from readiness import check_document_readiness  # Import our local readiness decision.

api_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset credential.
if not api_key:  # Check that authentication is configured.
    raise SystemExit("Set AGENTSET_API_KEY in this terminal first.")  # Stop when the key is missing.

namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Use our existing namespace.
job_id = input("Paste the completed job ID: ").strip()  # Accept the job ID without editing the script.

try:  # Let the test script display results and failures.
    documents = get_job_documents(job_id, namespace_id, api_key)  # Retrieve documents belonging to this exact job.
    readiness = check_document_readiness(documents)  # Evaluate the returned documents without another API call.
    print("Readiness:", readiness["state"])  # Display the workflow decision.
    print("Message:", readiness["message"])  # Explain the decision.
    print("Document IDs:", readiness["document_ids"])  # Display the IDs allowed for later retrieval.
    print("Documents found:", len(documents))  # Display the number of matching documents.
    for document in documents:  # Inspect each returned document.
        print("\nDocument ID:", document["id"])  # Display the identifier needed for document-specific retrieval.
        print("Job ID:", document["ingestJobId"])  # Confirm its association with the requested submission.
        print("Name:", document.get("name"))  # Display the document name when provided.
        print("Total chunks:", document.get("totalChunks"))  # Show whether searchable chunks were reported.
        print("Completed at:", document.get("completedAt"))  # Display any completion timestamp.
        print("Error:", document.get("error") or "None reported")  # Display any document-processing error.
except requests.exceptions.RequestException as error:  # Catch HTTP, connection, and timeout failures.
    print("Document lookup failed:", error)  # Distinguish request failure from finding no documents.
except ValueError as error:  # Catch invalid JSON or unexpected response data.
    print("Document response could not be processed:", error)  # Explain the response-validation problem.