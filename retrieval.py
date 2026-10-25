import requests  # Use the existing HTTP library to communicate with Agentset.


def retrieve_chunks(question, namespace_id, api_key, document_ids=None):  # Optionally limit retrieval to selected documents.
    url = f"https://api.agentset.ai/v1/namespace/{namespace_id}/search"  # Build the search endpoint for the supplied namespace.
    headers = {"Authorization": f"Bearer {api_key}"}  # Authenticate with the supplied API key.
    payload = {"query": question, "topK": 5, "includeMetadata": True}  # Request up to five chunks with source metadata.
    search_document_ids = None  # Leave retrieval unrestricted unless document IDs are supplied.

    if document_ids is not None:  # Apply restrictions when the caller supplies document IDs.
        if not isinstance(document_ids, list) or not document_ids:  # Require a nonempty list.
            raise ValueError("Supply a nonempty list of document IDs.")  # Prevent an unintended unrestricted search.
        if not all(isinstance(item, str) and item.strip() for item in document_ids):  # Validate every supplied identifier.
            raise ValueError("Every document ID must be a nonblank string.")  # Reject invalid identifiers.
        search_document_ids = [item.strip().removeprefix("doc_") for item in document_ids]  # Match the ID format observed in search metadata.
        if not all(search_document_ids):  # Reject an identifier consisting only of the prefix.
            raise ValueError("Document IDs must contain a value after the doc_ prefix.")  # Stop before sending an invalid filter.
        payload["filter"] = {"documentId": {"$in": search_document_ids}}  # Search only the approved documents.

    response = requests.post(url, headers=headers, json=payload, timeout=30)  # Send one search request and store its response.
    response.raise_for_status()  # Raise an error if the HTTP request failed.
    data = response.json()  # Convert the returned JSON into Python data.

    if not isinstance(data, dict):  # Check the outer response structure.
        raise ValueError("Agentset response must be a JSON object.")  # Report an unexpected response structure.
    chunks = data.get("data")  # Extract the returned chunk collection.
    if not isinstance(chunks, list):  # Check that the collection is a list.
        raise ValueError("Agentset response must contain a data list.")  # Reject missing or malformed results.
    if not all(isinstance(chunk, dict) for chunk in chunks):  # Validate the structure of every chunk.
        raise ValueError("Agentset returned a chunk with an unexpected format.")  # Reject malformed chunk entries.

    if search_document_ids is not None:  # Verify document ownership for a restricted search.
        for chunk in chunks:  # Inspect every returned chunk.
            metadata = chunk.get("metadata")  # Read the source information.
            if not isinstance(metadata, dict) or metadata.get("documentId") not in search_document_ids:  # Check against the normalized approved IDs.
                raise ValueError("Retrieved chunk does not belong to the selected documents.")  # Block unrelated or unverifiable evidence.

    return chunks  # Return validated chunks without displaying them.