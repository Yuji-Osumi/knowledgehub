# Docker 設計方針（KnowledgeHub）

## 目的

本ドキュメントは、KnowledgeHub における Docker / Docker Compose の設計意図を明確化し、
「なぜこの構成になっているのか」を将来の自分・第三者が理解できるようにすることを目的とする。

---

## 採用方針（結論）

* Docker は **開発体験の安定化と再現性確保** のために導入
* 本番構成を過度に意識せず、まずは **理解できる最小構成** を優先
* Backend + DB（PostgreSQL）+ Redis までを対象とした **開発用構成** とする
* 将来的な拡張（Frontend / CI / 本番構成）を妨げない設計を維持

---

## コンテナ構成

### 1. backend（FastAPI アプリケーション）
- Python 3.12
- FastAPI + Uvicorn
- JWT 認証処理
- API エンドポイント提供

### 2. db（PostgreSQL）
- PostgreSQL 16
- アプリケーションデータの永続化
- Alembic マイグレーション対象

### 3. redis（Redis）
- Redis 7
- セッションストア管理
- ユーザーセッション情報の保存・取得

---

## Dockerfile の責務

Dockerfile は以下のみを責務とする。

* Python / FastAPI 実行環境の定義
* 依存関係（requirements.txt）のインストール
* アプリケーション起動コマンドの明示

### ポイント

* `WORKDIR /app` により実行基準点を固定
* アプリケーションは `app.main:app` として起動
* 設定値や環境差分（env）は **Dockerfile に書かない**

👉 Dockerfile = **実行環境の定義書**

---

## docker-compose.yml の責務

Docker Compose は以下を担う。

* 複数コンテナ（backend / db / redis）の起動定義
* 環境変数の注入（env_file）
* 開発時の利便性向上（port / volume）
* サービス間接続（service 名による名前解決）

### compose をルートに置く理由

```text
knowledgehub/
├── docker-compose.yml
├── backend/
└── frontend（将来）
```

* プロジェクト全体の構成を俯瞰できる
* Backend / DB / Redis / Frontend を同一レイヤで束ねられる
* infra 的な責務を 1 箇所に集約できる

---

## 環境変数（.env）設計方針

### 基本方針

* `.env` は **環境依存情報の Single Source of Truth**
* backend / db / redis の全てから参照される
* アプリは必要な環境変数のみを信頼する

### .env の役割分担

* **POSTGRES_***
  * PostgreSQL コンテナ初期化用

* **DATABASE_URL**
  * FastAPI / SQLAlchemy / Alembic 用

* **REDIS_URL**
  * Redis 接続用（例: `redis://redis:6379/0`）

* **SESSION_TIMEOUT_HOURS**
  * セッション有効期限（デフォルト: 24 時間）

### 補足

* アプリ側の Settings では `extra="ignore"` を指定
* アプリは自分に不要な env を意識しない

👉 **Docker とアプリの責務分離を明確化**

---

## volumes 設計（開発用）

### Backend（bind mount）

```yaml
volumes:
  - ./backend/app:/app/app
```

* ソースコード変更を即時反映
* ホットリロード前提の開発体験を確保
* イメージ再ビルド回数を削減

### DB（named volume）

```yaml
volumes:
  postgres_data:
```

* DB データを Docker 管理領域に永続化
* コンテナ削除後もデータを保持
* ホストに DB 実体を露出させない

👉 **コードとデータで volume の種類を使い分ける**

---

## DB をコンテナ分離した理由

* アプリケーションと DB の責務を明確に分離するため
* 開発環境の再現性を高めるため
* Alembic を用いたマイグレーション検証を実 DB で行うため

### PostgreSQL コンテナ設計のポイント

* 初期ユーザー・DB は `POSTGRES_USER / POSTGRES_DB` により作成
* デフォルトの `postgres` ユーザーが存在しない場合がある
* backend からは service 名（`db`）で接続

👉 **「接続ユーザーは必ずしも postgres ではない」ことを理解する**

---

## Redis をコンテナとして追加した理由

* **セッションストア管理**のため
  - セッションデータの保存（key: `session:{session_id}`）
  - TTL による自動削除管理
  - ログアウト時の即座の削除

* **将来の拡張**に備える
  - Phase 2：ユーザー登録・メール検証トークン管理
  - キャッシング、レート制限等

### Redis コンテナ設計のポイント

* データ永続化は不要（TTL 管理のみ）
* backend からは service 名（`redis`）で接続
* 接続 URL：`redis://redis:6379/0`

👉 **ステートフル設計で必要なセッション管理を Redis で実現**

---

## この設計で得られたこと

* Docker を「おまじない」にせず説明できる
* env / volume / build の責務分離が明確になった
* 実務レベルの Docker Compose 構成を経験できた
* 将来的な構成変更に耐えられる基盤を構築できた

---

## 今後の拡張予定

* Frontend コンテナ追加
* dev / prod 用 compose 分離
* CI における Docker build / test 実行
