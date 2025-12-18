# Backend（Python / FastAPI）実装方針

## 目的

本ドキュメントは、KnowledgeHub Backend における **Python / FastAPI の実装判断を即決できる指針** を定める。

MVP 前提のため、構造は最小限とし、
必要になった時点でのみ分割・厳格化を行う。

---

## 採用技術

* Python
* FastAPI
* SQLAlchemy（ORM）
* Pydantic
* PostgreSQL

---

## ディレクトリ構成方針

### 初期（MVP開始時）

```txt
backend/
└─ app/
   └─ main.py
```

* すべて `main.py` に書いてよい
* router / service / repository 分割は行わない

---

### 分割を検討するタイミング

以下の **いずれかを満たした場合のみ** 分割を検討する。

* `main.py` が 300 行を超えた
* エンドポイントが 10 個を超えた
* 同じ処理のコピペが 3 回以上出現した

👉 分割は **一部から段階的に行う**

---

## API 設計

* パスは名詞・複数形
* ネストは 1 階層まで

```txt
GET    /notes
POST   /notes
GET    /notes/{note_id}
PUT    /notes/{note_id}
DELETE /notes/{note_id}
```

---

## Request / Response 方針

### Request

* Pydantic Model を必ず使用する
* validation は Model に寄せる

```python
class NoteCreateRequest(BaseModel):
    title: str
    content: str
```

---

### Response

* DB Model をそのまま返さない
* Response 専用 Model を定義する

```python
class NoteResponse(BaseModel):
    id: int
    title: str
```

---

## DB / ORM 方針

* ORM を基本とする
* 生 SQL は理由がある場合のみ使用する
* セッション管理は FastAPI の依存性で行う

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## エラーハンドリング

* FastAPI 標準の `HTTPException` を使用する
* ステータスコードは意味に沿って選択する

```python
if note is None:
    raise HTTPException(status_code=404, detail="Note not found")
```

---

## 型ヒント方針

* 戻り値の型は可能な限り書く
* MVP 段階では一部省略を許容する

```python
def get_note(note_id: int) -> NoteResponse:
    ...
```

---

## lint / 静的解析

### 方針

* 目的は **事故防止**
* 実装速度を落とさない

---

### 採用ツール（MVP）

* black：フォーマッタ（必須）
* ruff：lint（必須）
* mypy：型チェック（任意）

---

### 運用ルール

* CI にはまだ組み込まない
* ローカルで手動実行する

```bash
black .
ruff check .
```

---

## 禁止事項（Backend）

* DB Model を API レスポンスに直接使用する
* 例外を握りつぶす
* 未使用 import / dead code の放置
* 理由のない生 SQL

---

## 判断に迷った場合

* 要件定義を満たしているか
* 今は MVP かどうか
* 後で分割・修正しやすいか

---

この方針は、
**FastAPI 実装を迷いなく前に進めるためのガイド**である。
