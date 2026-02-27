import json
from pathlib import Path


class IDMapStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.data: dict[str, dict] = {}

    def load(self) -> None:
        if not self.path.exists():
            self.data = {}
            return
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def set(self, index_id: int, payload: dict) -> None:
        self.data[str(index_id)] = payload

    def get(self, index_id: int) -> dict | None:
        return self.data.get(str(index_id))

    def remove_ids(self, index_ids: list[int]) -> None:
        to_remove = {str(idx) for idx in index_ids}
        self.data = {k: v for k, v in self.data.items() if k not in to_remove}

    def find_indices_by_face_id(self, face_id: str) -> list[int]:
        out: list[int] = []
        for k, v in self.data.items():
            if v.get("face_id") == face_id:
                out.append(int(k))
        return sorted(out)

    def find_indices_by_user_id(self, user_id: str) -> list[int]:
        out: list[int] = []
        for k, v in self.data.items():
            if v.get("user_id") == user_id:
                out.append(int(k))
        return sorted(out)
