# KnowledgeHub

## 概要
ナレッジ共有・検索を目的とした個人開発プロジェクトです。
バックエンドは FastAPI を用いて REST API を構築しています。

## 技術スタック
### Backend
- **Language:** Python 3.12
- **Framework:** FastAPI
- **Validation / Settings:** Pydantic v2 / pydantic-settings
- **Database:** SQLAlchemy / PostgreSQL（予定）

### Infrastructure / Tooling
- **Environment:** Windows + WSL2 (Ubuntu)
- **Logging:** logging.dictConfig + RichHandler（local）
- **Infrastructure:** Docker / Docker Compose（予定）

## アプリ基盤設計の方針

### 設定管理（Settings）
- `BaseSettings` をベースに環境別設定を分離
- `local / dev / prod` を `APP_ENV` により切り替え
- `.env` を用いた安全な設定管理

### 例外ハンドリング方針
- アプリ独自の基底例外 `AppException` を定義
- 業務例外（NotFound / Validation / Unauthorized / Conflict）を明示
- 共通レスポンス形式でクライアントへ返却
- 想定外例外は 500 エラーとして一括ハンドリング

```json
  // 404エラーの場合
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": {},
  }
```

## 開発状況
- [x] Python 環境構築
- [x] FastAPI 初期化・起動確認
- [x] アプリ基盤設定
- [ ] DB 設計・実装
- [ ] API 実装

## 起動方法 (WSLで実行)
```bash
# Knowaledgehubディレクトリ直下で実行

# 仮想環境の有効化（WSL）
source .venv/bin/activate

# サーバー起動
uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000

# health check
curl http://localhost:8000/api/health

# docs
# http://localhost:8000/api/docs
```
