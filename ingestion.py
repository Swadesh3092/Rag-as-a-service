from urllib.parse import urlsplit  # Use Python's built-in URL parser.
import requests  # Reuse our existing HTTP library.

def create_ingest_job(document_url, namespace_id, api_key):  # Submit a document URL for processing.
    document_url = document_url.strip()  # Remove accidental spaces around the URL.
    parsed_url = urlsplit(document_url)  # Separate the URL into its main parts.
    if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:  # Check the URL's basic structure.
        raise ValueError("Enter a complete HTTP or HTTPS document URL.")  # Reject invalid input before making a request.
    endpoint = f"https://api.agentset.ai/v1/namespace/{namespace_id}/ingest-jobs"  # Select the namespace's ingestion endpoint.
    headers = {"Authorization": f"Bearer {api_key}"}  # Authenticate with the supplied key.
    payload = {"payload": {"type": "CRAWL", "url": document_url}}  # Prepare the same ingestion payload used by the dashboard.
    response = requests.post(endpoint, headers=headers, json=payload, timeout=30)  # Send the request and store Agentset's HTTP response.
    response.raise_for_status()  # Check the stored response for an HTTP error.  # Stop if the API rejects the request.
    data = response.json()  # Read the API response as Python data.
    if not isinstance(data, dict) or data.get("success") is not True:  # Check that the response reports success.
        raise ValueError("Agentset did not return a successful ingestion response.")  # Reject an unexpected response.
    job = data.get("data")  # Extract the created ingestion job.
    if not isinstance(job, dict):  # Check that the job has the expected structure.
        raise ValueError("Agentset did not return an ingestion job object.")  # Report missing job details.
    if not isinstance(job.get("id"), str) or not job["id"].strip():  # Check that we received a usable job identifier.
        raise ValueError("Agentset did not return a valid job ID.")  # Stop because status checking needs this identifier.
    if not isinstance(job.get("status"), str) or not job["status"].strip():  # Check that the response contains a status.
        raise ValueError("Agentset did not return a valid job status.")  # Report incomplete job details.
    return job  # Return the job without claiming that processing is complete.

def get_ingest_job(job_id, namespace_id, api_key):  # Retrieve the current details of an existing ingestion job.
    endpoint = f"https://api.agentset.ai/v1/namespace/{namespace_id}/ingest-jobs/{job_id}"  # Select the specific job.
    headers = {"Authorization": f"Bearer {api_key}"}  # Authenticate with the supplied key.
    response = requests.get(endpoint, headers=headers, timeout=30)  # Read the job without creating another one.
    response.raise_for_status()  # Raise an error if the request failed.
    data = response.json()  # Convert the response into Python data.
    if not isinstance(data, dict) or data.get("success") is not True:  # Check that the API reports success.
        raise ValueError("Agentset did not return a successful job response.")  # Reject an unexpected response.
    job = data.get("data")  # Extract the job details.
    if not isinstance(job, dict):  # Check the returned job structure.
        raise ValueError("Agentset did not return a job object.")  # Report missing job details.
    if job.get("id") != job_id:  # Confirm that the response describes the requested job.
        raise ValueError("Agentset returned an unexpected job ID.")  # Stop if the identifiers do not match.
    if not isinstance(job.get("status"), str) or not job["status"].strip():  # Check that the job contains a usable status.
        raise ValueError("Agentset did not return a valid job status.")  # Report incomplete response data.
    return job  # Return the details for the caller to inspect.


def get_job_documents(job_id, namespace_id, api_key):  # Find every document associated with one ingestion job.
    endpoint = f"https://api.agentset.ai/v1/namespace/{namespace_id}/documents"  # Select the namespace's document-list endpoint.
    headers = {"Authorization": f"Bearer {api_key}"}  # Authenticate with the supplied key.
    params = {"ingestJobId": job_id, "perPage": 100}  # Request documents belonging to this job.
    documents = []  # Collect documents across all result pages.
    seen_cursors = set()  # Track cursors to detect a repeated pagination response.

    while True:  # Fetch pages until Agentset reports no more results.
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)  # Read one page of matching documents.
        response.raise_for_status()  # Raise an error if the request failed.
        data = response.json()  # Convert the response into Python data.
        if not isinstance(data, dict) or data.get("success") is not True:  # Check that the API reports a successful response.
            raise ValueError("Agentset did not return a successful document-list response.")  # Reject an unexpected response.
        page = data.get("data")  # Extract this page's documents.
        if not isinstance(page, list):  # Check that documents are supplied as a list.
            raise ValueError("Agentset did not return a document list.")  # Report malformed response data.
        for document in page:  # Validate each document before collecting it.
            if not isinstance(document, dict) or document.get("ingestJobId") != job_id:  # Confirm the document belongs to this job.
                raise ValueError("Agentset returned an unexpected document or job association.")  # Prevent mixing unrelated documents.
            if not isinstance(document.get("id"), str) or not document["id"].strip():  # Check that the document has a usable identifier.
                raise ValueError("Agentset returned a document without a valid ID.")  # Stop because later retrieval needs this ID.
        documents.extend(page)  # Add the validated documents to our collection.
        pagination = data.get("pagination")  # Read the pagination details.
        if not isinstance(pagination, dict) or not isinstance(pagination.get("hasMore"), bool):  # Check whether pagination information is usable.
            raise ValueError("Agentset returned invalid pagination details.")  # Avoid silently returning an incomplete list.
        if not pagination["hasMore"]:  # Check whether we have reached the final page.
            return documents  # Return all matching documents, including an empty list if none exist.
        cursor = pagination.get("nextCursor")  # Read the position of the next page.
        if not isinstance(cursor, str) or not cursor or cursor in seen_cursors:  # Reject missing or repeated cursors.
            raise ValueError("Agentset returned an invalid or repeated next cursor.")  # Stop an incomplete or endless pagination sequence.
        seen_cursors.add(cursor)  # Remember the cursor before following it.
        params["cursor"] = cursor  # Request the next page on the following loop.