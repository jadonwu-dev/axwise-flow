import types

from backend.services.results.repositories import AnalysisResultRepository
from backend.models import AnalysisResult, InterviewData


class _FakeQuery:
    def __init__(self):
        self.called = []
        self._result = object()

    def join(self, *args, **kwargs):
        self.called.append(("join", args, kwargs))
        return self

    def filter(self, *args, **kwargs):
        self.called.append(("filter", args, kwargs))
        return self

    def first(self):
        self.called.append(("first", (), {}))
        return self._result


class _FakeSession:
    def __init__(self, q=None):
        self._q = q or _FakeQuery()
        self.last_query_model = None

    def query(self, model):
        self.last_query_model = model
        return self._q


def test_analysis_result_repository_get_by_id_constructs_expected_query():
    q = _FakeQuery()
    fake_db = _FakeSession(q)

    repo = AnalysisResultRepository(fake_db)
    res = repo.get_by_id(396, user_id="user_123")

    # Should return whatever .first() returns
    assert res is q._result

    # Query should be built against AnalysisResult
    assert fake_db.last_query_model is AnalysisResult

    # Verify join and filter were invoked with expected shapes
    op_names = [name for (name, _, _) in q.called]
    assert op_names[:2] == ["join", "filter"], op_names

    # The join should reference InterviewData
    join_calls = [c for c in q.called if c[0] == "join"]
    assert join_calls, "Expected a join call"
    assert InterviewData in join_calls[0][1], f"Join args: {join_calls[0][1]}"

    # The filter should be called with two conditions (result_id and user_id)
    filter_calls = [c for c in q.called if c[0] == "filter"]
    assert filter_calls, "Expected a filter call"
    assert len(filter_calls[0][1]) == 2, f"Filter args: {filter_calls[0][1]}"

