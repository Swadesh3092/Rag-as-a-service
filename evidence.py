def build_evidence(chunks):  # Turn retrieved chunks into labelled evidence and traceable sources.
    evidence_parts = []  # Collect the labelled passages for the model.
    sources = {}  # Map each label to its original passage and source details.
    for chunk in chunks:  # Process each retrieved chunk in its returned order.
        text = chunk.get("text") or ""  # Read the passage while allowing missing or empty text.
        if not text.strip():  # Check whether the passage contains usable text.
            continue  # Skip blank passages without assigning a label.
        label = f"S{len(sources) + 1}"  # Assign the next consecutive source label.
        evidence_parts.append(f"[{label}]\n{text}")  # Attach the label to the full passage.
        sources[label] = {  # Record the original content behind this label.
            "chunk_id": chunk.get("id"),  # Preserve Agentset's chunk identifier when available.
            "text": text,  # Preserve the full passage for evidence inspection.
            "metadata": dict(chunk.get("metadata") or {}),  # Copy the supplied source metadata.
        }  # Finish this source record.
    evidence = "\n\n".join(evidence_parts)  # Combine the labelled passages into one string.
    return evidence, sources  # Return model-ready evidence and its source mapping.