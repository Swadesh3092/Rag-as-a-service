import os  # Read API keys from the terminal environment.
import requests  # Communicate with Agentset and Groq.
from evidence import build_evidence  # Reuse our tested evidence-preparation function.
from retrieval import retrieve_chunks
from generation import generate_answer  # Reuse our tested Groq generation function.


agentset_key = os.environ.get("AGENTSET_API_KEY", "").strip()  # Load the Agentset credential.
groq_key = os.environ.get("GROQ_API_KEY", "").strip()  # Load the Groq credential.
if not agentset_key or not groq_key:  # Check that both services have credentials.
    raise SystemExit("Set AGENTSET_API_KEY and GROQ_API_KEY in this terminal first.")  # Stop if either key is missing.

question = "How many runs did BB McCullum personally score in the Royal Challengers Bangalore versus Kolkata Knight Riders match on 2008-04-18?"  # Test refusal when individual batting runs are absent from the evidence.
namespace_id = "ns_cmvikgl67000104l5nz0twae4"  # Select the collection containing matches.csv.
fallback = "I couldn't find enough information in the retrieved evidence to answer that."  # Define the insufficient-evidence response.
stage = "Agentset retrieval"  # Identify the current stage for error reporting.

try:  # Handle failures across the connected workflow.
    chunks = retrieve_chunks(question, namespace_id, agentset_key)  # Fetch evidence using the reusable retrieval function.
    print(f"Chunks returned: {len(chunks)}")  # Show how many chunks were returned.

    stage = "Evidence preparation"  # Identify the local processing stage for error reporting.
    evidence, sources = build_evidence(chunks)  # Prepare labelled passages and their source mapping.
    for label, source in sources.items():  # Visit each source to display its supporting passage.
        metadata = source["metadata"]  # Read the preserved source details.
        print(f"\n[{label}] File: {metadata.get('filename', 'unknown')} | Chunk: {metadata.get('sequence_number', 'unknown')}")  # Show where the passage came from.
        print(source["text"])  # Display the full passage for verification.

    if not evidence:  # Check whether any usable evidence was prepared.
        print("\nAnswer:", fallback)  # Return the fallback without calling Groq.
    else:  # Generate an answer when usable evidence is available.
        stage = "Groq generation"  # Identify this stage if an error occurs.
        answer, finish_reason = generate_answer(question, evidence, groq_key)  # Ask Groq to answer using our prepared evidence.
        print("\nAnswer:", answer)  # Display the returned answer.
        print("Finish reason:", finish_reason)  # Show whether generation completed normally.

except requests.exceptions.RequestException as error:  # Catch HTTP, network, and timeout failures.
    print(f"{stage} failed: {error}")  # Identify which service request failed.
except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:  # Catch unexpected data formats.
    print(f"{stage} returned an unexpected format: {error}")  # Identify where processing failed.