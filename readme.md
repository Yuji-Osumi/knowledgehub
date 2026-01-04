# KnowledgeHub

## 概要
ナレッジ共有・検索を目的とした個人開発プロジェクトです。
バックエンドは FastAPI を用いて REST API を構築しています。

## 技術スタック
### Backend
- **Language:** Python 3.12
- **Framework:** FastAPI
- **Validation / Settings:** Pydantic v2 / pydantic-settings
- **Database:** SQLAlchemy / PostgreSQL（Docker コンテナ）

### Infrastructure / Tooling
- **Environment:** Windows + WSL2 (Ubuntu)
- **Logging:** logging.dictConfig + RichHandler（local）
- **Infrastructure:** Docker / Docker Compose

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

## 起動方法 (WSLで実行)
```bash
# 仮想環境の有効化（WSL）
source .venv/bin/activate

# プロジェクトルートで実行
docker compose  up --build

# health check
curl http://localhost:8000/api/health

# docs
# http://localhost:8000/api/docs
```
# Docker 操作ガイド

```bash
docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```
# テーブル確認
```sql
\dt
```
**注意：** `POSTGRES_USER` は `.env` で定義した値を使用してください。

---

## マイグレーション（Alembic）

### 最新 revision まで適用

```bash
docker compose exec backend alembic upgrade head
```

### 新しい revision を作成

```bash
docker compose exec backend alembic revision -m "add xxx table"
```


## 追記
### スペルチェック (cSpell)
プロジェクトのタイポ（綴りミス）を防止するために [cSpell](https://cspell.org/) を導入しています。

#### VS Code で開発する場合
推奨拡張機能の **"Code Spell Checker"** をインストールしてください。
インストール後、エディタ上でスペルミスが青い波線でハイライトされるようになります。

#### 独自用語の追加
プロジェクト固有の単語（専門用語や固有名詞など）がエラーになる場合は、`cspell.config.yaml` の `words` セクションに追加してください。

## Docker
Docker / Docker Compose を **開発環境の再現性確保と実行手順の明確化** を目的として導入しています。
詳細な設計意図については以下を参照してください。
docs/03_実装方針/08_Docker 設計方針.md


## 開発状況
- [x] Python 環境構築
- [x] FastAPI 初期化・起動確認
- [x] アプリ基盤設定
- [x] SQLAlchemy + Alembic 基盤セットアップ
  - Settings に DB 設定追加（DATABASE_URL）
  - Engine / Session 設計
  - Declarative Base + TimestampMixin 定義
  - sample モデル作成（疎通確認用）
  - Alembic 初期マイグレーション作成・適用
- [x] Docker / Docker Compose 導入
  - Dockerfile 作成
  - docker-compose.yml 作成
  - コンテナ起動確認（/docs 表示）
- [ ] API 実装
