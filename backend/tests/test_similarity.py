import math
import pytest
from app.services.similarity import cosine_similarity


def test_identical_vectors_have_perfect_similarity():
    """Identical vectors should yield a cosine similarity of 1.0."""
    vec = [1.0, 2.0, 3.0, 4.0]
    score = cosine_similarity(vec, vec)
    assert math.isclose(score, 1.0, rel_tol=1e-5)


def test_orthogonal_vectors_have_zero_similarity():
    """Perpendicular (orthogonal) vectors should yield 0.0."""
    vec_a = [1.0, 0.0]
    vec_b = [0.0, 1.0]
    score = cosine_similarity(vec_a, vec_b)
    assert math.isclose(score, 0.0, abs_tol=1e-5)


def test_opposite_vectors_have_negative_one_similarity():
    """Opposite vectors pointing in reverse directions should yield -1.0."""
    vec_a = [1.0, 0.0]
    vec_b = [-1.0, 0.0]
    score = cosine_similarity(vec_a, vec_b)
    assert math.isclose(score, -1.0, rel_tol=1e-5)


def test_zero_vector_returns_zero_without_error():
    """A zero vector (magnitude 0) should safely return 0.0 without division by zero."""
    vec_zero = [0.0, 0.0, 0.0]
    vec_normal = [1.0, 2.0, 3.0]
    assert cosine_similarity(vec_zero, vec_normal) == 0.0
    assert cosine_similarity(vec_normal, vec_zero) == 0.0


def test_empty_vectors_raise_value_error():
    """Passing empty lists must raise a ValueError."""
    with pytest.raises(ValueError, match="Vectors cannot be empty"):
        cosine_similarity([], [1.0, 2.0])

    with pytest.raises(ValueError, match="Vectors cannot be empty"):
        cosine_similarity([1.0, 2.0], [])


def test_dimension_mismatch_raises_value_error():
    """Vectors of different dimensions cannot be compared."""
    vec_3d = [1.0, 2.0, 3.0]
    vec_2d = [1.0, 2.0]
    with pytest.raises(ValueError, match="Vector dimension mismatch: 3 != 2"):
        cosine_similarity(vec_3d, vec_2d)


def test_embedding_ranking_order():
    """Verify that candidate ranking properly sorts candidates by relevance."""
    # Simulated 2D embedding space:
    # Query is close to target (angle is small) and far from distractors
    query_vec = [1.0, 1.0]
    relevant_doc_vec = [0.9, 1.1]       # Close direction
    unrelated_doc_vec = [-1.0, 0.5]     # Far direction

    score_relevant = cosine_similarity(query_vec, relevant_doc_vec)
    score_unrelated = cosine_similarity(query_vec, unrelated_doc_vec)

    assert score_relevant > score_unrelated

    # Ensure ranking descending sort behaves as expected
    candidates = [
        ("unrelated", score_unrelated),
        ("relevant", score_relevant),
    ]
    ranked = sorted(candidates, key=lambda x: x[1], reverse=True)
    assert ranked[0][0] == "relevant"