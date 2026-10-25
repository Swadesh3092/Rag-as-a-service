def check_document_readiness(documents):  # Decide whether all supplied documents are ready for retrieval.
    if not documents:  # Handle a job whose documents are not available yet.
        return {"state": "waiting", "message": "No documents are available yet. Check again shortly.", "document_ids": []}  # Keep retrieval blocked.

    for document in documents:  # Check all documents for reported failures first.
        if document.get("error") or document.get("failedAt"):  # Detect a processing error or failure timestamp.
            return {"state": "failed", "message": "A document failed to process.", "document_ids": []}  # Report failure without enabling retrieval.

    for document in documents:  # Check whether every document has completed processing.
        if not document.get("completedAt"):  # Detect a document without a completion timestamp.
            return {"state": "waiting", "message": "Documents are still processing. Check again shortly.", "document_ids": []}  # Wait for processing to finish.

    for document in documents:  # Inspect chunk counts after all documents have completed.
        chunk_count = document.get("totalChunks")  # Read the reported number of searchable chunks.
        if type(chunk_count) is not int or chunk_count <= 0:  # Require a positive integer count rather than assuming missing data means success.
            return {"state": "empty", "message": "Processing completed, but searchable chunks could not be confirmed.", "document_ids": []}  # Keep empty or unverified documents blocked.

    document_ids = [document["id"] for document in documents]  # Collect the identifiers already validated by get_job_documents.
    return {"state": "ready", "message": "Documents have completed processing and contain searchable chunks.", "document_ids": document_ids}  # Return the IDs that retrieval may use.