from app.schemas import TaskCreate
import pytest

def test_normalized_lines_valid():
    t = TaskCreate(lines="victoria, central")
    assert t.normalized_lines() == "victoria,central"

def test_normalized_lines_invalid():
    t = TaskCreate(lines="victoria, nope")
    with pytest.raises(ValueError):
        t.normalized_lines()
