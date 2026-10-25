import os  # Read credentials from the terminal environment.
import requests  # Identify HTTP and network failures.
import streamlit as st  # Build the browser interface.
from ingestion import create_ingest_job, get_ingest_job, get_job_documents  # Reuse our tested ingestion functions.
from readiness import check_document_readiness  # Evaluate document processing readiness.
from pipeline import answer_question  # Reuse our document-question-answering workflow.


st.title("Document Q&A")  # Display the application title.
st.caption("Add a public document URL, check its status, then ask questions about it.")  # Explain the workflow.

agentset_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Read the Agentset credential.
groq_key = os.environ.get("GROQ_API_KEY", "").strip()  # Read the Groq credential.
namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Use our existing document collection.

st.subheader("Add a document")  # Introduce document submission.
st.caption("Use a public document URL that opens without signing in. Preview links may ingest webpage text instead of the file.")  # Explain the input limitation.

with st.form("document_form"):  # Keep document submission separate from question submission.
    document_url = st.text_input("Document URL")  # Collect the URL.
    ingest_submitted = st.form_submit_button("Add document")  # Submit only when this button is clicked.

if ingest_submitted:  # Handle an explicit document submission.
    st.session_state.pop("approved_document_ids", None)  # Clear the previous document selection.
    st.session_state.pop("ingestion_job", None)  # Remove the old job so it cannot be approved accidentally.
    st.session_state.pop("readiness_result", None)  # Remove the previous readiness decision.
    st.session_state.pop("qa_result", None)  # Clear an answer belonging to the previous submission.
    st.session_state.pop("answered_question", None)  # Clear the previous answer's question.
    st.session_state.pop("submitted_document_url", None)  # Remove the previous submission's URL.

    if not document_url.strip():  # Check for an empty URL.
        st.warning("Please enter a document URL.")  # Explain the missing input.
    elif not agentset_key:  # Check the credential needed for ingestion.
        st.error("Set AGENTSET_API_KEY in the terminal, then restart the app.")  # Explain missing configuration.
    else:  # Continue when the required inputs are present.
        try:  # Handle submission failures.
            with st.spinner("Submitting your document..."):  # Show progress during the creation request.
                job = create_ingest_job(document_url, namespace_id, agentset_key)  # Submit the URL using our tested function.
            st.session_state["ingestion_job"] = job  # Remember the returned job.
            st.session_state["submitted_document_url"] = document_url.strip()  # Remember the URL associated with this job.
            st.success("Document submitted. Click Check status to follow its processing.")  # Confirm acceptance without claiming readiness.
        except requests.exceptions.RequestException:  # Catch HTTP, connection, and timeout failures.
            st.error("Submission could not be confirmed. Check Agentset Jobs before retrying; a job may already exist.")  # Avoid encouraging duplicate submissions.
        except ValueError as error:  # Catch invalid input or unexpected response data.
            st.error(str(error))  # Display the validation message.

if "ingestion_job" in st.session_state:  # Show status controls for the current submission.
    st.write("Submitted URL:", st.session_state.get("submitted_document_url", ""))  # Identify the document being processed.

    if st.button("Check status"):  # Refresh details only when requested.
        st.session_state.pop("approved_document_ids", None)  # Require a fresh readiness decision.
        st.session_state.pop("readiness_result", None)  # Clear the previous readiness result.
        st.session_state.pop("qa_result", None)  # Clear previous output while readiness is rechecked.
        st.session_state.pop("answered_question", None)  # Clear the question associated with previous output.

        if not agentset_key:  # Check authentication before making requests.
            st.error("Agentset API key is missing. Restart the app with the key configured.")  # Explain the configuration problem.
        else:  # Continue when authentication is available.
            try:  # Handle status and document lookup failures.
                saved_job = st.session_state["ingestion_job"]  # Read the current submission's job.
                with st.spinner("Checking processing and document readiness..."):  # Show progress during the checks.
                    updated_job = get_ingest_job(saved_job["id"], namespace_id, agentset_key)  # Read the current job status.
                    st.session_state["ingestion_job"] = updated_job  # Save the latest successfully received job details.
                    if updated_job["status"] == "COMPLETED":  # Inspect documents after the job completes.
                        documents = get_job_documents(updated_job["id"], namespace_id, agentset_key)  # Find documents belonging to this job.
                        readiness = check_document_readiness(documents)  # Check completion, failures, and chunk availability.
                        st.session_state["readiness_result"] = readiness  # Remember the decision for display.
                        if readiness["state"] == "ready":  # Approve documents only when readiness passes.
                            st.session_state["approved_document_ids"] = readiness["document_ids"]  # Save the IDs permitted for retrieval.
            except requests.exceptions.RequestException:  # Catch failures communicating with Agentset.
                st.error("The check could not complete. Questions remain blocked; try Check status again.")  # Avoid using stale document approvals.
            except (ValueError, KeyError, TypeError) as error:  # Catch unexpected response structures.
                st.error(f"The status response could not be processed: {error}")  # Explain why readiness was not established.

    saved_job = st.session_state["ingestion_job"]  # Read the last known job details.
    status = saved_job["status"]  # Read the last known processing status.

    if status == "COMPLETED":  # Display document readiness separately from job completion.
        readiness = st.session_state.get("readiness_result")  # Read the document-level decision when available.
        if st.session_state.get("approved_document_ids"):  # Check whether documents passed readiness validation.
            st.success("Document processing is complete. You can ask questions below.")  # Enable the user to continue.
        elif readiness:  # Explain a document-level readiness problem.
            st.warning(readiness["message"])  # Display the reason questions remain blocked.
        else:  # Handle a completed job that has not passed document checks.
            st.info("The job completed. Click Check status to verify its documents.")  # Request the remaining readiness check.
    elif status == "FAILED":  # Handle a reported job failure.
        st.error("Document processing failed.")  # Explain the processing outcome.
        st.write("Details:", saved_job.get("error") or "No error details provided.")  # Show available failure information.
    else:  # Handle queued, processing, or other unapproved statuses.
        st.info(f"Last known status: {status}. Click Check status again shortly.")  # Explain how to refresh processing details.

    with st.expander("Technical details"):  # Keep internal identifiers outside the main user flow.
        st.write("Job ID:", saved_job["id"])  # Display the job identifier for debugging.
        st.write("Last known job status:", status)  # Display the most recently received status.
        st.write("Approved document IDs:", st.session_state.get("approved_document_ids", []))  # Display the current retrieval scope.

st.divider()  # Separate document ingestion from question answering.
st.subheader("Ask a question")  # Introduce the Q&A section.

can_ask = bool(st.session_state.get("approved_document_ids"))  # Allow questions only when document IDs have been approved.

if not can_ask:  # Explain why the Ask button is disabled.
    st.caption("Add a document and check its status before asking questions.")  # Guide the user to the required step.

with st.form("question_form"):  # Submit questions independently of document ingestion.
    question = st.text_input("Your question")  # Collect the user's question.
    submitted = st.form_submit_button("Ask", disabled=not can_ask)  # Block submission until documents are ready.

if submitted:  # Handle an explicit question submission.
    st.session_state.pop("qa_result", None)  # Clear the previous answer before attempting another.
    st.session_state.pop("answered_question", None)  # Clear the previous answer's question.
    approved_ids = st.session_state.get("approved_document_ids")  # Read the current approved document selection.

    if not question.strip():  # Reject an empty question before making requests.
        st.warning("Please enter a question.")  # Explain the missing input.
    elif not agentset_key or not groq_key:  # Check both credentials required for Q&A.
        st.error("Set AGENTSET_API_KEY and GROQ_API_KEY in the terminal, then restart the app.")  # Explain missing configuration.
    elif not approved_ids:  # Recheck document restrictions before running the pipeline.
        st.warning("Check document readiness before asking a question.")  # Prevent unrestricted retrieval.
    else:  # Continue when the question, credentials, and document selection are available.
        try:  # Handle retrieval and generation failures.
            with st.spinner("Finding evidence and preparing your answer..."):  # Show progress during the pipeline.
                result = answer_question(question, namespace_id, agentset_key, groq_key, document_ids=approved_ids)  # Answer using only the approved documents.
            st.session_state["qa_result"] = result  # Preserve the returned answer and sources across reruns.
            st.session_state["answered_question"] = question.strip()  # Remember which question produced this answer.
        except requests.exceptions.RequestException:  # Catch HTTP, connection, and timeout failures.
            st.error("A service request failed. Please try again.")  # Report failure without showing credentials.
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):  # Catch unexpected response data or ownership validation failures.
            st.error("The answer could not be prepared. Check the pipeline's input and response formats.")  # Distinguish processing failure from insufficient evidence.

if "qa_result" in st.session_state:  # Display the most recent successful pipeline result.
    result = st.session_state["qa_result"]  # Read the saved answer and source mapping.
    st.caption(f"Question: {st.session_state['answered_question']}")  # Associate the output with its original question.
    st.subheader("Answer")  # Label the generated answer.
    st.write(result["answer"])  # Display the answer or insufficient-evidence response.

    if result["finish_reason"] == "length":  # Detect generation that reached its token limit.
        st.warning("The answer may be incomplete because generation reached its limit.")  # Make truncated output visible.

    st.subheader("Retrieved evidence")  # Label all passages supplied to generation.
    if not result["sources"]:  # Handle a result without usable evidence.
        st.caption("No usable passages were retrieved.")  # Explain why there are no source expanders.

    for label, source in result["sources"].items():  # Display each passage supplied to the model.
        metadata = source.get("metadata") or {}  # Read preserved source details when available.
        source_name = metadata.get("filename") or metadata.get("page_url") or "Document"  # Support both uploaded-file and URL-ingested sources.
        chunk_number = metadata.get("sequence_number", "unknown")  # Read the original chunk number.
        with st.expander(f"[{label}] {source_name} | Chunk {chunk_number}"):  # Let users inspect individual passages.
            st.text(source.get("text", ""))  # Display the retrieved passage as plain text.
            st.caption(f"Document ID: {metadata.get('documentId', 'unknown')}")  # Expose the source association for verification.