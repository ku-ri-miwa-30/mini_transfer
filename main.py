
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
# health_check()は何のために使用するか不明
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
# デコレーター上でstatus_codeを記述することで成功したときにこの値が帰るようになる
# デコレーター：URLの指定。正常動作した場合のステータスコード201(作成できた場合に返すもの)
@app.post("/files", status_code=201)
# awaitを関数内部で使用しているのでasyncを付ける。申請ボタンを押したときにUploadfileの型で受け取る
async def upload_file(file: UploadFile):
    # 拡張子チェック
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="拡張子に誤りがあります")

    # ファイルサイズをチェック
    global next_id
    file_id = next_id
    # 保存先のパスを生成する
    path = STORAGE / f"{file_id}_{file.filename}"
    # アップロードされたファイルの中身を bytes で読み出す。時間がかかるかもしれない処理なので await で待つ
    content = await file.read()
    # 読みだされた中身をlen()で取得する
    size = len(content)

    # サイズチェック
    if size == 0:
        raise HTTPException(status_code=400, detail="ファイルが空です")

    # その bytes を path（例：storage/1_hello.txt）に書き込む
    # 受け取った中身を、サーバーのフォルダに保存する
    path.write_bytes(content)

    # filesのリストに今回アップロードされたファイルを追加している
    files.append({"id": file_id, "name": file.filename, "path": str(path), "size": size})

    # 次に使用するIDの値を更新
    next_id += 1
    return {"id": file_id, "name": file.filename, "size": size}

# ---------------------------------------------------------------
# Mission 3：一覧
#   GET /files で、アップロード済みファイルの一覧を返す
#   - 各要素は {"id", "name", "size"} の3つ（path は返さない）
#   - 1件もなければ []
# ---------------------------------------------------------------
@app.get("/files")
def list_files():
    # グローバルで保持しているリストから全件取得する
    return [{"id": f["id"], "name": f["name"], "size": f["size"]} for f in files]

# ---------------------------------------------------------------
# Mission 4：ダウンロード
#   GET /files/{file_id} でファイル本体を返す
#   - 見つからなければ 404
# ---------------------------------------------------------------
# デフォルトで正常終了すれば200が返却されるのでデコレーターにはstatus_codeの指定を行わない。
@app.get("/files/{file_id}")
def download(file_id: int):
    # 引数として渡されたidに一致するリストを検索する
    for f in files:
        if f["id"] == file_id:
            # ヒットした場合はFileResponseというfastAPIの型で返却する。
            # filenameはダウンロードされるときに保存される名前。
            return FileResponse(f["path"], filename=f["name"])
    raise HTTPException(status_code=404, detail="ファイルが見つかりません")
# ---------------------------------------------------------------
# Mission 5：削除
#   DELETE /files/{file_id} でファイルを削除する
#   - 成功したら 204（中身なし）
#   - リストからも、STORAGE のファイル本体からも消す
#   - 見つからなければ 404
# ---------------------------------------------------------------
# 成功した場合は204を返却
@app.delete("/files/{file_id}", status_code=204)
def delete(file_id: int):
    # 削除対象のファイルを検索、ヒットしたら削除実施
    for f in files:
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
