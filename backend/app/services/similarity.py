import math

def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Formula:
        similarity = (A * B) / (||A|| * ||B||)
        where:
            A . B = sum(a * b for a, b in zip(A, B))
            ||A|| = sqrt(sum(a ** 2 for a in A))
    """

    if not vec_a or not vec_b:
        raise ValueError("Vectors cannot be empty")

    if len(vec_a) != len(vec_b):
        raise ValueError(
            f"Vector dimension mismatch: {len(vec_a)} != {len(vec_b)}"
        )

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)