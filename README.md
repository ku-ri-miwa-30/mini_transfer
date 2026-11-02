# ミニファイル授受アプリ トレーニング：Step 1

テストに合格するまで自分でコードを書く「ドリル形式」です。
答えのコードは入っていません。詰まったら下のヒントを1段ずつ開き、それでもだめなら質問してください。

## 準備（最初の1回だけ）

```bash
cd mini-transfer
python -m venv .venv
# Mac / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## 進め方

1. `main.py` を開き、Mission 1 の TODO を実装する
2. そのミッションだけテストする

   ```bash
   pytest -k m1
   ```

3. 緑（passed）になったら、Swagger UIでも触ってみる

   ```bash
   uvicorn main:app --reload
   ```

   ブラウザで http://localhost:8000/docs を開く

4. 次のミッションへ。最後に `pytest` だけで全部が緑になればStep 1クリア

赤（failed）になったら、エラーの `assert` の行を読んで「期待値」と「実際の値」を比べるのがコツです。

## ルール

- 1ミッション＝15〜30分が目安。30分詰まったらヒントを見る
- Copilotは補完までOK。チャットで丸ごと生成させるのはStep 1では禁止
- 書いたコードは、1行ずつ「なぜこう書くか」を声に出して説明できる状態にする
- 全部クリアしたら `main.py` をチャットに貼ってください。コードレビューします

## ミッション一覧

| No. | 内容 | テスト |
| --- | --- | --- |
| 1 | `GET /health` で生存確認 | `pytest -k m1` |
| 2 | `POST /files` でアップロード | `pytest -k m2` |
| 3 | `GET /files` で一覧 | `pytest -k m3` |
| 4 | `GET /files/{file_id}` でダウンロード | `pytest -k m4` |
| 5 | `DELETE /files/{file_id}` で削除 | `pytest -k m5` |
| 6 | 拡張子チェックと空ファイルチェック | `pytest -k m6` |

## ヒント

<details><summary>Mission 1 ヒント</summary>

- `@app.get("/health")` を付けた関数を作る
- 辞書を `return` すれば、FastAPIが自動でJSONにしてくれる
</details>

<details><summary>Mission 2 ヒント①：受け取り方</summary>

- 引数を `file: UploadFile` にすると、アップロードされたファイルを受け取れる
- 中身は `await file.read()` で bytes として取れる。`await` を使うので関数は `async def` にする
- ファイル名は `file.filename`
- 201にするには `@app.post("/files", status_code=201)`
</details>

<details><summary>Mission 2 ヒント②：保存と id</summary>

- 保存先は `STORAGE / f"{file_id}_{file.filename}"`（同じ名前のファイルが来ても上書きされない）
- 書き込みは `path.write_bytes(content)`
- size は `len(content)`
- id は今は `len(files) + 1` で動く。ただしMission 5で問題になる（後述）
</details>

<details><summary>Mission 3 ヒント</summary>

- `files` の各要素から `id`、`name`、`size` だけを取り出したリストを返す
- リスト内包表記：`[{"id": f["id"], ...} for f in files]`
- path を返さないのは、サーバー内部の場所を外に見せないため（セキュリティの基本）
</details>

<details><summary>Mission 4 ヒント</summary>

- URLの `{file_id}` は、同じ名前の引数 `file_id: int` で受け取れる。型を書くと数字以外は自動で弾かれる
- `files` を for で回して id が一致するものを探す
- 見つかったら `FileResponse(path, filename=name)` を返す
- 見つからなければ `raise HTTPException(status_code=404, detail="...")`
- 探す処理はMission 5でも使うので、`find_file(file_id)` のような関数に分けておくと楽
</details>

<details><summary>Mission 5 ヒント①：削除</summary>

- `@app.delete("/files/{file_id}", status_code=204)`。204は「中身なし」なので何も return しない
- 本体の削除は `Path(path).unlink()`
- リストからの削除は `files.remove(対象の辞書)`
</details>

<details><summary>Mission 5 ヒント②：id が重複する問題</summary>

`test_m5_id_not_reused_after_delete` が落ちるはずです。

id=1, 2 を作って 1 を消すと、`len(files) + 1` はまた 2 になり、既存の id=2 とかぶります。
`main.py` に用意してある `next_id`（次に使う番号）を使う方法を考えてみてください。
グローバル変数を関数の中で書き換えるときは `global next_id` が必要です。
（next_id はテストのたびに 1 に戻るので、テスト同士が影響し合うことはありません）
</details>

<details><summary>Mission 6 ヒント</summary>

- 拡張子は `Path(file.filename).suffix` で取れる（`".txt"` のようにドット付き）
- 大文字の `.PDF` も許可したいので `.lower()` を使う
- チェックは保存する「前」に行う。順番を間違えるとテストが落ちる
- 失敗時は `raise HTTPException(status_code=400, detail="...")`
</details>

## おまけ課題（テストなし）

- Pydanticの `BaseModel` で `FileOut(id, name, size)` を定義し、`response_model` を指定する。Swagger UIの表示がどう変わるか見る
- 400エラーの `detail` を「許可されていない拡張子です：.exe」のように、原因が分かる文章にする

Step 1 をクリアしたら、Step 2（SQLite＋SQLAlchemy）のドリルに進みます。
