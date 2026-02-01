# 例外処理ポリシー（Backend）

## 目的

本ドキュメントは、KnowledgeHub Backend における
**API 例外処理・エラーレスポンス・ログ出力の統一方針**を定める。

- 実装時の判断基準を明確にする
- エラーレスポンス形式を安定させる
- フロントエンドとの連携を容易にする

ことを目的とする。

---

## 基本方針

- 例外は **握りつぶさず、必ずログとレスポンスに反映する**
- 想定内のエラーと想定外のエラーを明確に分離する
- エラーレスポンスは **常に同一フォーマット**で返す
- ステータスコードと意味を一致させる

---

## エラーレスポンス形式（共通）

すべての API エラーは、以下の JSON 形式を基本とする。

```json
"error": {
  "code": "ERROR_CODE",
  "message": "エラーメッセージ",
  "details": {}
}
```

### 各フィールドの役割

* `code`

  * システム内部で識別可能なエラーコード
  * フロントエンドの分岐処理・ログ集計に使用
* `message`

  * ユーザーに表示可能なエラーメッセージ
* `details`

  * 任意の詳細情報（バリデーション失敗箇所など）
  * 通常は空、または `null`

※ スタックトレースや内部例外情報は **レスポンスに含めない**

---

## 例外の分類

### 1. 業務例外（想定内エラー）

ユーザー操作や入力によって発生しうるエラー。
アプリ独自の基底例外 `AppException` を継承して表現する。

#### 代表的な例外

| 例外クラス        | HTTP | 用途                 |
| ----------------- | ---- | -------------------- |
| ValidationError   | 400  | 入力値不正           |
| NotFoundError     | 404  | リソースが存在しない |
| UnauthorizedError | 401  | 未認証               |
| ConflictError     | 409  | 重複・状態不整合     |

---

### 2. 想定外例外

* プログラムの不具合
* 設定ミス
* 外部依存の障害

これらは **500 Internal Server Error** として一括処理する。

---

## ステータスコード方針

### 400 VALIDATION_ERROR

* 入力値が不正
* バリデーションエラー

### 401 Unauthorized

* 認証が必要なリソースへの未ログインアクセス

### 403 Forbidden

* 認証済みだが権限不足

### 404 Not Found

* 指定されたリソースが存在しない

### 409 Conflict

* 重複登録
* 状態不整合

### 500 Internal Server Error

* 想定外の例外
* サーバー内部エラー

👉 クライアントには **一般的なメッセージのみ返却する**

## バリデーションエラー（400）の扱い

FastAPI / Pydantic による入力バリデーションエラーは、
**400 Bad Request として統一フォーマットで返却する**。

### 実装

`RequestValidationError` ハンドラで 422 → 400 に変換：

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,  # FastAPI 標準の 422 を 400 に変換
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": exc.errors(),
            }
        },
    )
```

### ステータスコード統一ルール

- **400 Bad Request** = クライアント入力不備（バリデーション失敗、形式エラー）
- **401 Unauthorized** = 認証不備（Cookie 未設定、セッション無効）
- **404 Not Found** = リソース不在 or 権限不足（情報隠蔽）
- **409 Conflict** = 業務的衝突（重複リソース、状態不整合など）

### 例

- 無効なメール形式 → 400 VALIDATION_ERROR
- パスワード強度不足 → 400 VALIDATION_ERROR
- メール重複登録 → 400 USER_ALREADY_EXISTS（カスタム 400 例外）

---

## FastAPI での実装方針

### 業務例外（推奨）

* `AppException` を継承した独自例外を使用する

```python
raise NotFoundError("Resource not found")
```

---

### FastAPI 標準例外

* FastAPI 内部・インフラ寄りの処理では `HTTPException` を使用してもよい
* 業務ロジックでは極力使用しない

---

### 例外ハンドラ

* `AppException` 用の共通ハンドラを定義
* ステータスコードに応じてログレベルを切り替える

#### ログ出力方針

| ステータス | ログレベル |
| ---------- | ---------- |
| 400 系     | WARNING    |
| 500 系     | ERROR      |

* local 環境では WARNING でもスタックトレースを出力する
* 本番環境では必要最小限に抑制する想定

---

### 想定外例外

* 個別に握りつぶさない
* 共通の `Exception` ハンドラで捕捉
* ログに ERROR として出力
* レスポンスは 500 に統一

---

## フロントエンドとの連携方針

* フロントエンドは `error_code` を主に判定に使用する
* `message` はユーザー表示用
* ステータスコードで大まかな分岐を行う

---

## 禁止事項

* `print` のみで例外を処理する
* エラーレスポンス形式を例外ごとに変える
* 内部例外情報をそのままクライアントに返す
* 業務ロジック内で無秩序に `HTTPException` を投げる

---

## 判断に迷った場合の指針

* このエラーは「想定内」か「想定外」か
* ユーザーに何を伝えるべきか
* フロントエンドは安定して扱えるか
* logging で十分な情報が残るか
