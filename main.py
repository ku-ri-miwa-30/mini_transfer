
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

next_id = 0  # 次に使う id（Mission 5 で必要になる。名前は変えない）

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
# デコレーター上でstatus_codeを記述することで成功したときにこの値が帰るようになる
@app.post("/files", status_code=201)
async def upload_file(file: UploadFile):
    ext = file.filename
    print(type(Path(ext)))
    print(ext)
    ext = Path(ext).suffix()

    if not ext in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400)
    if len(file) == 0:
        raise HTTPException(status_code=400)

    global next_id
    file_id = next_id
    path = STORAGE / f"{file_id}_{file.filename}"
    # 何をしている？
    path.write_bytes(await file.read())
    # filesのリストに今回アップロードされたファイルを追加している
    size = file.size
    files.append({"id": file_id, "name": file.filename, "path": str(path), "size": size})
    print(f"size は {size}")
    print(f"ファイルリストの中身を表示する{files}")
    print(f"next_id は {next_id}")
    next_id += 1
    print(f"next_id は {next_id}")
    return {"id": file_id, "name": file.filename, "size": size}


# ---------------------------------------------------------------
# Mission 3：一覧
#   GET /files で、アップロード済みファイルの一覧を返す
#   - 各要素は {"id", "name", "size"} の3つ（path は返さない）
#   - 1件もなければ []
# ---------------------------------------------------------------
@app.get("/files")
def list_files():
    return [{"id": f["id"], "name": f["name"], "size": f["size"]} for f in files]

# ---------------------------------------------------------------
# Mission 4：ダウンロード
#   GET /files/{file_id} でファイル本体を返す
#   - 見つからなければ 404
# ---------------------------------------------------------------
@app.get("/files/{file_id}", status_code=200)
def download(file_id: int):
    for f in files:
        if f["id"] == file_id:
            return FileResponse(f["path"], filename=f["name"])
    print("該当するものがありません")
    raise HTTPException(status_code=404, detail="ファイルが見つかりません")
# ---------------------------------------------------------------
# Mission 5：削除
#   DELETE /files/{file_id} でファイルを削除する
#   - 成功したら 204（中身なし）
#   - リストからも、STORAGE のファイル本体からも消す
#   - 見つからなければ 404
# ---------------------------------------------------------------
@app.delete("/files/{file_id}", status_code=204)
def delete(file_id: int):
    # i=0
    # for i, f in enumerate(files):
        
    #     print(f"f : {f}")
    #     if f["id"] == file_id:
    #         files.pop(i)
    #         # Path(f).unlink()
    # return HTTPException(status_code=404, detail="ファイルが見つかりません")

    for f in files:
        print(f"f : {f}")
        if f["id"] == file_id:
            files.remove(f)
            Path(f["path"]).unlink()
            return

    raise HTTPException(status_code=404, detail="ファイルが見つかりません")

# ---------------------------------------------------------------
# Mission 6：入力チェック（Mission 2 のアップロードに追加する）
#   - 拡張子が ALLOWED_EXTENSIONS 以外なら 400
#   - 中身が空（0バイト）なら 400
#   - エラーのときは保存もしないし、リストにも入れない
# ---------------------------------------------------------------
