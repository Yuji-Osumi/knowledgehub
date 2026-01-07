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
- `local / dev / prod` を `backend/.env`の`APP_ENV` により安全な設定切り替え

### 環境別プロファイルと挙動
システムの挙動は、`APP_ENV` 環境変数によって以下のように自動的に切り替わります。

| 項目             | local                     | dev                | prod         |
| :--------------- | :------------------------ | :----------------- | :----------- |
| **Debug モード** | `True` (詳細なエラー表示) | `False`            | `False`      |
| **ログレベル**   | `DEBUG`                   | `INFO`             | `INFO`       |
| **用途**         | ローカル開発・デバッグ    | 検証環境・動作確認 | 本番稼働環境 |

### サービス起動時の検証
アプリケーション起動時、現在どのプロファイルが適用されているかをログで即座に確認できます。設定ミスによる「本番環境でのデバッグモード有効化」などを防ぐための仕様です。

```text
INFO      Logging initialized with level: INFO                   logging.py:67
INFO      Application startup | Environment: prod, Debug: False  main.py:59
```

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

### DB マイグレーション
DB スキーマ変更は Alembic により管理する。
models 変更後は revision を作成し、DB へ反映する。

## 起動方法 (WSLで実行)

本プロジェクトでは 各種操作を Makefile 経由で行う。詳しくは`\Makefile`を参照すること
```bash
# 仮想環境の有効化（WSL）
source .venv/bin/activate

# docker
make up       # docker起動
make ps       # docker状態確認

# # DB / Alembic
make psql     # DB 接続 \dtでテーブル確認
make migrate  # データベースの構成を最新化
make revision msg="hoge" # マイグレーションファイルを作成

# health check
make health-all   # /api/health にリクエストして疎通確認

# docs
# http://localhost:8000/api/docs
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
- Backend コンテナは bind mount を利用
- PostgreSQL は named volume（postgres_data）を利用

詳細な設計意図については以下を参照してください。

```docs/03_実装方針/08_Docker 設計方針.md```


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
