from fastapi.testclient import TestClient
import uvicorn
from app import main


class FakeTable:
    def __init__(self, data):
        self._data = data

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def order(self, *a, **k):
        return self

    def limit(self, n):
        return self

    def execute(self):
        class R:
            def __init__(self, data):
                self.data = data

        return R(self._data)


class FakeDB:
    def __init__(self, data):
        self._data = data

    def table(self, name):
        return FakeTable(self._data)


fake_data = [{"artist": "Local Test Artist", "listeners": 42, "captured_at": "2026-01-01T00:00:00Z"}]

# Inject fake DB so endpoints work offline
main.supabase_db = FakeDB(fake_data)


if __name__ == "__main__":
    uvicorn.run(main.app, host="127.0.0.1", port=8000)
