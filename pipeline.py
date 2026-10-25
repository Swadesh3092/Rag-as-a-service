from retrieval import retrieve_chunks  # Import the function that searches Agentset.
from evidence import build_evidence  # Import the function that prepares labelled passages.
from generation import generate_answer  # Import the function that calls Groq.

def answer_question(question, namespace_id, agentset_key, groq_key, document_ids=None):  # Coordinate Q&A with optional document restrictions.
    question = question.strip()  # Remove spaces around the question.
    if not question:  # Check whether the user supplied a meaningful input.
        raise ValueError("Please enter a question.")  # Stop before making API calls for a blank question.
    chunks = retrieve_chunks(question, namespace_id, agentset_key, document_ids=document_ids)  # Forward the selected document IDs to retrieval.
    evidence, sources = build_evidence(chunks)  # Prepare the model's evidence and its source mapping.
    if not evidence:  # Check whether any usable passages were retrieved.
        return {  # Return a result without calling Groq.
            "answer": "I couldn't find enough information in the retrieved evidence to answer that.",  # Explain that evidence is insufficient.
            "sources": sources,  # Preserve the source mapping returned by evidence preparation.
            "finish_reason": None,  # Indicate that no model generation occurred.
        }  # Finish the no-evidence result.
    answer, finish_reason = generate_answer(question, evidence, groq_key)  # Generate an answer using the prepared evidence.
    return {  # Keep the answer and its supporting sources together.
        "answer": answer,  # Return the model's answer.
        "sources": sources,  # Return all passages supplied to the model, including any it did not cite.
        "finish_reason": finish_reason,  # Return the model's completion status.
    }  # Finish the generated result.