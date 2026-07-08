"""RAG Agent — fetches learning content for the concept.

This is a STUB retriever: it returns a single placeholder document. Replace
`retrieve()` with a real vector-store lookup (e.g. pgvector / Chroma) later.
"""


def retrieve(concept: str) -> list[dict]:
    # TODO: plug a vector store here (embed `concept`, similarity search a corpus).
    return [
        {
            "title": f"Reference notes: {concept}",
            "content": (
                f"Key ideas and worked intuition about '{concept}'. "
                "(RAG stub — replace with retrieved course material.)"
            ),
        }
    ]


async def rag_node(state, config):
    return {"docs": retrieve(state["concept"])}
