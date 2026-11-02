"""テスト用の準備（このファイルは編集しなくてOK）

テストのたびに保存先を一時フォルダに切り替え、files を空にし、next_id を 1 に戻すので、
テスト同士が影響し合わず、storage フォルダも汚れない。
"""

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "STORAGE", tmp_path)
    main.files.clear()
    monkeypatch.setattr(main, "next_id", 1)
    return TestClient(main.app)
