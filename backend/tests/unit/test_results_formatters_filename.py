from backend.services.results.formatters import get_filename_for_data_id


class _Row:
    def __init__(self, filename):
        self.filename = filename


class _FakeQuery:
    def __init__(self, row):
        self._row = row

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._row


class _FakeDB:
    def __init__(self, row):
        self._row = row

    def query(self, _model):
        return _FakeQuery(self._row)


def test_get_filename_found():
    db = _FakeDB(_Row("file1.txt"))
    assert get_filename_for_data_id(db, 123) == "file1.txt"


def test_get_filename_missing_returns_unknown():
    db = _FakeDB(None)
    assert get_filename_for_data_id(db, 123) == "Unknown"


def test_get_filename_no_id_returns_unknown():
    db = _FakeDB(_Row("file1.txt"))
    assert get_filename_for_data_id(db, None) == "Unknown"

