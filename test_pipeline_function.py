import os  # Read credentials from the current terminal environment.
import requests  # Identify network and HTTP errors.
from pipeline import answer_question  # Import the new workflow entry point.

agentset_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset key.
groq_key = os.environ.get("GROQ_API_KEY", "").strip()  # Load the Groq key.
if not agentset_key or not groq_key:  # Check that both credentials are available.
    raise SystemExit("Set AGENTSET_API_KEY and GROQ_API_KEY in this terminal first.")  # Stop if a credential is missing.

question = "What text does this document contain?"  # Ask a question supported by the dummy PDF.  # Ask a question supported by our small test PDF.
namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Select the namespace containing matches.csv.

try:  # Let the caller decide how to display results and failures.
    print("Question sent:", question)  # Confirm which question the pipeline receives.
    result = answer_question(question, namespace_id, agentset_key, groq_key, document_ids=["doc_lvghrqg8o0gri2vx9afnmh5o"])  # Run Q&A using only the verified PDF.
    print("Answer:", result["answer"])  # Display the returned answer in the terminal.
    print("Finish reason:", result["finish_reason"])  # Display the generation status.
    for label, source in result["sources"].items():  # Display the mapping for each passage supplied to Groq.
        print("Source text:", source.get("text"))  # Inspect the passage associated with this source label.
        metadata = source["metadata"]  # Read the preserved source details.
        print(f"[{label}] File: {metadata.get('filename', 'unknown')} | Chunk: {metadata.get('sequence_number', 'unknown')}")  # Connect each label to its original source.
except requests.exceptions.RequestException as error:  # Catch failures when communicating with either service.
    print(f"Service request failed: {error}")  # Report a request failure rather than claiming no evidence was found.
except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:  # Catch invalid input or unexpected data formats.
    print(f"Pipeline could not complete: {error}")  # Display the processing failure.