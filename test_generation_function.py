import os  # Read the Groq key from the terminal environment.
import requests  # Identify request failures.
from generation import generate_answer  # Import our extracted generation function.

api_key = os.environ.get("GROQ_API_KEY", "").strip()  # Load the Groq credential.
if not api_key:  # Check that the key is available.
    raise SystemExit("Set GROQ_API_KEY in this terminal first.")  # Stop when authentication is missing.

evidence = "[S1]\n## Dummy PDF file"  # Reproduce the exact short evidence involved in the refusal.
questions = ["What text does this document contain?", "Who was player of the match in the first IPL match?"]  # Test a supported request and an unsupported fact.

for question in questions:  # Run each test independently.
    print(f"\nQuestion: {question}")  # Show which question is being tested.
    try:  # Let the caller handle failures from the function.
        answer, finish_reason = generate_answer(question, evidence, api_key)  # Generate an answer using the extracted function.
        print("Answer:", answer)  # Display the returned answer.
        print("Finish reason:", finish_reason)  # Display whether generation completed normally.
    except requests.exceptions.RequestException as error:  # Catch HTTP, network, and timeout failures.
        print(f"Generation request failed: {error}")  # Describe the request failure.
    except (ValueError, KeyError, IndexError, TypeError) as error:  # Catch an unexpected response format.
        print(f"Generation response could not be read: {error}")  # Describe the response-processing failure.