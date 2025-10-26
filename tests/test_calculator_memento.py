import pytest
import pandas as pd
from app.calculator_memento import Memento, Caretaker


# --- Tests for Memento ---

def test_memento_stores_copy_not_reference():
    """Ensure Memento stores a deep copy of the DataFrame."""
    df = pd.DataFrame({"a": [1, 2, 3]})
    m = Memento(df)
    assert not m.snapshot is df
    assert m.snapshot.equals(df)

    # modifying original should not affect snapshot
    df.loc[0, "a"] = 99
    assert m.snapshot.loc[0, "a"] == 1


# --- Fixtures for Caretaker ---

@pytest.fixture
def caretaker():
    return Caretaker()


@pytest.fixture
def df():
    return pd.DataFrame({"a": [1, 2], "b": [3, 4]})


# --- Tests for Caretaker.save() ---

def test_save_adds_memento_and_clears_redos(caretaker, df):
    """save() adds a Memento and clears the redo stack."""
    caretaker._redos.append(Memento(df))
    caretaker.save(df)
    assert len(caretaker._undos) == 1
    assert caretaker._redos == []


# --- Tests for can_undo() / can_redo() ---

@pytest.mark.parametrize("undos,expected", [([], False), ([1], True)])
def test_can_undo(undos, expected):
    c = Caretaker()
    c._undos = undos
    assert c.can_undo() == expected


@pytest.mark.parametrize("redos,expected", [([], False), ([1], True)])
def test_can_redo(redos, expected):
    c = Caretaker()
    c._redos = redos
    assert c.can_redo() == expected


# --- Tests for undo() ---

def test_undo_success(caretaker, df):
    """undo() should restore last snapshot and move current_df to redos."""
    caretaker.save(df)
    df2 = pd.DataFrame({"a": [9], "b": [8]})
    restored = caretaker.undo(df2)
    assert isinstance(restored, pd.DataFrame)
    assert restored.equals(df)
    assert len(caretaker._redos) == 1


def test_undo_empty_raises(caretaker, df):
    """undo() raises IndexError when no undos available."""
    with pytest.raises(IndexError, match="Nothing to undo"):
        caretaker.undo(df)


# --- Tests for redo() ---

def test_redo_success(caretaker, df):
    """redo() should restore last redo snapshot and move current_df to undos."""
    caretaker._redos.append(Memento(df))
    df2 = pd.DataFrame({"a": [99], "b": [88]})
    restored = caretaker.redo(df2)
    assert isinstance(restored, pd.DataFrame)
    assert restored.equals(df)
    assert len(caretaker._undos) == 1


def test_redo_empty_raises(caretaker, df):
    """redo() raises IndexError when no redos available."""
    with pytest.raises(IndexError, match="Nothing to redo"):
        caretaker.redo(df)
