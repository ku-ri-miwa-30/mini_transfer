"""ミニファイル授受アプリ Step 1：REST API と FastAPI

ルール
- TODO の部分を自分で実装する（関数名やURLは自由に追加してOK）
- 下の STORAGE、files、next_id という名前は変えない（テストが使うため）
- STORAGE は関数の中で毎回 STORAGE として参照する
- 1ミッション書いたら `pytest -k m1` のように、そのミッションだけテストする
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse

app = FastAPI(title="ミニファイル授受")

STORAGE = Path("storage")  # アップロードしたファイルの保存先
STORAGE.mkdir(exist_ok=True)

# アップロードしたファイルの情報を入れておくリスト（Step 2でDBに置き換える）
# 1件の形の例：{"id": 1, "name": "hello.txt", "size": 5, "path": "storage/1_hello.txt"}
files: list[dict] = []

next_id = 1  # 次に使う id（Mission 5 で必要になる。名前は変えない）

ALLOWED_EXTENSIONS = {".txt", ".csv", ".pdf"}


# ---------------------------------------------------------------
# Mission 1：生存確認API
#   GET /health にアクセスすると {"status": "ok"} を返す
# ---------------------------------------------------------------
# TODO
@app.get("/health")
def health_check():
    return {"status" : "ok"}


# ---------------------------------------------------------------
# Mission 2：アップロード
#   POST /files でファイルを受け取り、STORAGE に保存する
#   - ステータスコードは 201
#   - 返すJSON：{"id": 1, "name": "hello.txt", "size": 5}
#   - id は 1, 2, 3... と増えていく
# ---------------------------------------------------------------
# TODO
# ここが何をしているのか不明
@app.post("/files", status_code=201)
async def upload_file(file):
    file_id = len(files)+1
    path = STORAGE / f"{file_id}_{file.filename}"
    # 何をしている？
    path.write_bytes(await file.read())
    # filesのリストに今回アップロードされたファイルを追加している
    files.append({"id": file_id, "name": file.filename, "path": str(path)})
    size = size(file)
    status_code = 201
    return {"id": file_id, "name": file.file_name, "size": size}


# ---------------------------------------------------------------
# Mission 3：一覧
#   GET /files で、アップロード済みファイルの一覧を返す
#   - 各要素は {"id", "name", "size"} の3つ（path は返さない）
#   - 1件もなければ []
# ---------------------------------------------------------------
# TODO
@app.get("/files")
def list_files():
    # path=
    return [{"id": ["id"], "name": ["name"]} for f in files]

# ---------------------------------------------------------------
# Mission 4：ダウンロード
#   GET /files/{file_id} でファイル本体を返す
#   - 見つからなければ 404
# ---------------------------------------------------------------
# TODO
@app.get("/files/{file_id}")
def download(file_id: int):
    for f in files:
        if ["id"] == file_id:
            status_code=200
            return FileResponse(["path"], filename=["name"])

    raise HTTPException(status_code=404, detail="ファイルが見つかりません")
# ---------------------------------------------------------------
# Mission 5：削除
#   DELETE /files/{file_id} でファイルを削除する
#   - 成功したら 204（中身なし）
#   - リストからも、STORAGE のファイル本体からも消す
#   - 見つからなければ 404
# ---------------------------------------------------------------
# TODO
@app.delete("/files/{file_id}")
def delete(file_id):
    for f in files:
        if ["file_id"] == file_id:
            files.pop(f)
            Path(f).unlink()
            return [{"status_code": 204}]
    return HTTPException(status_code=404, detail="ファイルが見つかりません")


# ---------------------------------------------------------------
# Mission 6：入力チェック（Mission 2 のアップロードに追加する）
#   - 拡張子が ALLOWED_EXTENSIONS 以外なら 400
#   - 中身が空（0バイト）なら 400
#   - エラーのときは保存もしないし、リストにも入れない
# ---------------------------------------------------------------
