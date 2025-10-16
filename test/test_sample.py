import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sample import add

def test_add():
    assert add(2, 3) == 5
