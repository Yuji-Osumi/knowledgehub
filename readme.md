# KnowledgeHub

![Lint](https://github.com/Yuji-Osumi/knowledgehub/actions/workflows/lint.yml/badge.svg)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-green)](https://yuji-osumi.github.io/knowledgehub/)
![FastAPI](https://img.shields.io/badge/FastAPI-0.127.0-teal)
![Docker](https://img.shields.io/badge/Docker-dockerized-blue)


## 概要
ナレッジ共有・検索を目的とした個人開発プロジェクトです。
バックエンドは FastAPI を用いて REST API を構築しています。

API仕様は OpenAPI として管理しており、エンドポイント定義やリクエスト例を Swagger UI 上で確認できます。

- 📘 **API仕様（OpenAPI / Swagger UI）**
  https://yuji-osumi.github.io/knowledgehub/

- 🗂 **開発進行状況詳細（WBS）**
  https://drive.google.com/drive/u/1/folders/1pDKpyoXqMJdgXl9hObzuUBB1klC8uHBq

※作業中のWBSの写しであるため最新情報でない恐れがあります

## 開発方針

**DevOpsを意識した「失敗しにくい構造」の実現**

開発者体験の向上と技術キャッチアップを目的に、人による確認や記憶に依存せず、
システムで失敗を防ぐ構造を重視しています。

- **Docker** — 開発環境を固定し、「手元で動かない」を防止
- **環境別設定** — `.env` で prod/dev/local を分離、機密情報を安全管理
- **Makefile** — 実行コマンドを明示・統一し、操作ミスを削減
- **静的検証** — ruff/mypy による自動チェックで、バグを早期発見
- **マイグレーション管理** — Alembic で DB 変更履歴をコード化
- **CI/CD** — GitHub Actions で品質を自動担保

これにより **変更 → 検証 → 巻き戻し** を安全に回せる開発フローを実現し、
**コードを仕様書とする開発** を実践しています。

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

### Frontend（UIスタブ）
- **Build Tool:** Vite
- **Framework:** React
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Routing:** React Router
- **Editor（予定）:** Tiptap

※ 現在は API 未接続の UI スタブ段階
※ 画面構成・URL 設計・画面遷移の検証を目的とする


## 起動方法 (WSLで実行)

本プロジェクトでは 各種操作を Makefile 経由で行う。詳しくは`\Makefile`を参照すること

```bash
# 仮想環境の有効化（WSL）
source .venv/bin/activate

# docker
make up       # docker起動
make ps       # docker状態確認

# DB / Alembic
make psql     # DB 接続 \dtでテーブル確認
make migrate  # データベースの構成を最新化
make revision msg="hoge" # マイグレーションファイルを作成

# health check
make health-all   # /api/health にリクエストして疎通確認

# frontendを起動 (UI stub)
make front   # http://localhost:5173

# docs
# http://localhost:8000/api/docs
```

## ディレクトリ構成（Backend）

```text
backend/
├── app/
│   ├── core/        # 設定管理・ロギング・例外定義
│   ├── db/          # DB設定・models・session
│   ├── api/         # ルーティング（今後追加予定）
│   └── main.py      # FastAPI エントリーポイント
├── alembic/         # DB マイグレーション管理
├── pyproject.toml   # Python / lint / mypy 設定
└── Dockerfile
```

- **core**：アプリ全体で共通となる関心事を集約
- **db**：DB接続・ORM定義・マイグレーション管理

## ディレクトリ構成（Frontend）

```text
frontend/ui-stub/src/
├── lib/          # 共通機能（API・認証・データ）
│   ├── api.ts        # API関数エクスポート
│   ├── mockApi.ts    # Mock API実装
│   ├── mockData.ts   # ダミーデータ
│   └── auth.tsx      # 認証コンテキスト
├── pages/        # 各画面コンポーネント
├── types/        # TypeScript型定義
└── App.tsx       # ルーティング定義
```

※ バックエンド API 未接続の UI スタブを以下の目的で導入しています

## UIスタブについて

### 目的
- バックエンドAPI実装前に画面構成・URL設計・画面遷移を検証
- API仕様の妥当性を実際の画面操作から逆算してフィードバック
- フロントエンド・バックエンド並行開発の準備

### 制約・前提
- **API未接続**: Mock API（遅延シミュレーション付き）を使用
- **データ非永続化**: 画面リロードでデータは初期化される
- **認証**: メモリベースの簡易実装（本番ではJWT予定）

### 動作確認
ゲストログイン機能により、入力不要で即座に動作確認可能

## ドキュメント構成

本プロジェクトでは、実装だけでなく **設計・意思決定・作業過程の可視化** を重視しています。
そのため、以下のようにドキュメントを体系的に管理しています。

```text
docs/
├── 01_要件定義/        # 目的・MVP・機能要件・非機能要件
├── 02_設計/            # DB設計（ERD）・API設計・アーキテクチャ
├── 03_実装方針/        # 実装ルール・設計判断の背景
├── 99_作業日報/        # 作業ログ・振り返り
└── old/                # 廃止・差し替え済みドキュメント
```

## 設定管理（Settings）
- `BaseSettings` をベースに環境別設定を分離
- `local / dev / prod` を `backend/.env`の`APP_ENV` により安全な設定切り替え

### 環境別プロファイルと挙動
システムの挙動は、`APP_ENV` 環境変数によって以下のように自動的に切り替わります。

| 項目             | local                     | dev                | prod         |
| :--------------- | :------------------------ | :----------------- | :----------- |
| **Debug モード** | `True` (詳細なエラー表示) | `False`            | `False`      |
| **ログレベル**   | `DEBUG`                   | `INFO`             | `INFO`       |
| **用途**         | ローカル開発・デバッグ    | 検証環境・動作確認 | 本番稼働環境 |

### 環境変数

| 変数名       | 説明                           | 例            |
| ------------ | ------------------------------ | ------------- |
| APP_ENV      | 実行環境（local / dev / prod） | local         |
| DATABASE_URL | DB 接続文字列                  | postgresql:// |

※ 実際の値は `.env` ファイルで管理し、リポジトリには含めません。


## サービス起動時の検証

アプリケーション起動時、現在どのプロファイルが適用されているかをログで即座に確認できます。設定ミスによる「本番環境でのデバッグモード有効化」などを防ぐための仕様です。

```log
INFO      Logging initialized with level: INFO                   logging.py:67
INFO      Application startup | Environment: prod, Debug: False  main.py:59
```

## API 設計方針

- REST API ベース（実装済み：記事CRUD）
- UUID ベースの public_id を URL パラメータに使用（セキュリティ考慮）
- 論理削除（is_valid フラグ）による監査証跡保持
- レイヤード構造（Router / Service / Repository）← 今後実装
- FastAPI の依存性注入（Depends）を活用
- レスポンス形式を統一し、例外は共通ハンドラで制御

### 実装済みエンドポイント
- `GET /api/articles` - 記事一覧
- `GET /api/articles/{public_id}` - 記事詳細
- `POST /api/articles` - 記事作成
- `PUT /api/articles/{public_id}` - 記事更新
- `DELETE /api/articles/{public_id}` - 記事削除

### 今後実装予定
- 認証エンドポイント（/api/auth/login, /api/auth/logout）

## 例外ハンドリング方針
- アプリ独自の基底例外 `AppException` を定義
- 業務例外（NotFound / Validation / Unauthorized / Conflict）を明示
- 共通レスポンス形式でクライアントへ返却
- 想定外例外は 500 エラーとして一括ハンドリング

```json
// 404エラーの場合
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": {}
  }
}
```

## DB マイグレーション
DB スキーマ変更は Alembic により管理する。
models 変更後は revision を作成し、DB へ反映する。

## CI（品質チェック）

本プロジェクトでは、コード品質と型安全性を担保するために GitHub Actions による CI を導入しています。

### 実行内容
- **Ruff**：Lint / 不要 import / コーディング規約チェック
- **mypy**：型チェック（strict 寄り設定）

### 実行タイミング
- push 時
- Pull Request 作成・更新時

```bash
make lint
```

上記コマンドで、CI と同一のチェックをローカルでも実行可能です。

## Docker

Docker / Docker Compose を **開発環境の再現性確保と実行手順の明確化** を目的として導入しています。

- Backend コンテナは bind mount を利用
- PostgreSQL は named volume（postgres_data）を利用

詳細な設計意図については以下を参照してください。

```docs/03_実装方針/08_Docker 設計方針.md```

## 追記

### スペルチェック (cSpell)
プロジェクトのタイポ（綴りミス）を防止するために [cSpell](https://cspell.org/) を導入しています。

#### VS Code で開発する場合
推奨拡張機能の **"Code Spell Checker"** をインストールしてください。
インストール後、エディタ上でスペルミスが青い波線でハイライトされるようになります。

#### 独自用語の追加
プロジェクト固有の単語（専門用語や固有名詞など）がエラーになる場合は、`cspell.config.yaml` の `words` セクションに追加してください。

## 開発状況

### 要件定義・設計
- [x] 目的・背景定義（ターゲットユーザー／課題整理）
- [x] MVP 範囲定義（必須機能／拡張機能の切り分け）
- [x] 機能要件定義（CRUD・検索・認証の整理）
- [x] 非機能要件定義（ログ／セキュリティ／運用方針）
- [x] ユースケース・操作フロー定義
- [x] 技術スタック選定理由の明文化
- [x] データモデル定義（ERD・テーブル一覧作成）
- [x] API 仕様設計（主要エンドポイント設計）

### プロジェクト準備
- [x] GitHub リポジトリ作成・初期構成
- [x] コーディング規約策定（Ruff / mypy）
- [x] ログ設計・例外処理ポリシー策定
- [x] セキュリティ方針整理（認証・入力バリデーション）
- [x] 非機能要件（性能・運用）整理

### バックエンド基盤
- [x] Python 環境構築
- [x] FastAPI 初期化・起動確認
- [x] アプリ基盤設定（Settings / Logging / Error Handling）
- [x] SQLAlchemy + Alembic 基盤セットアップ
- [x] Docker / Docker Compose 導入
‐ [x] Makefile 導入
  - Docker / DB / Lint / Health Check などの操作をコマンド統一
- [x] 開発用 CI 初期設定（Lint / Type Check）
  - GitHub Actions workflow 作成
  - Ruff / mypy を push / PR 時に自動実行
 - [x] 記事管理 API 実装（CRUD）
  - GET /api/articles - 記事一覧取得
  - GET /api/articles/{public_id} - 記事詳細取得
  - POST /api/articles - 記事新規作成
  - PUT /api/articles/{public_id} - 記事更新
  - DELETE /api/articles/{public_id} - 記事削除（論理削除）

### フロントエンド（UIスタブ）
- [x] Vite + React + TypeScript 初期構成
- [x] Tailwind CSS 導入
- [x] React Router による画面遷移定義
- [x] 型定義作成（User / Article / Tag / Folder）
- [x] Mock API 実装（遅延シミュレーション付き）
  - 記事CRUD（取得・保存・削除）
  - 認証（ログイン・ログアウト・ユーザー登録）
- [x] 認証コンテキスト・保護ルーティング実装
- [x] UIスタブ作成（全6画面）
  - ログイン／新規登録／記事一覧／記事詳細／記事フォーム／404
  - ゲストログイン機能（動作試験用）
- [x] API 設計へのフィードバック整理

### 今後の予定
- [x] API 実装（CRUD）
- [ ] 認証・認可（JWT）
- [ ] 検索機能（全文検索）
- [ ] テスト（pytest / E2E）
- [ ] OpenAPI 設計の明文化

## AI 利用方針

本プロジェクトでは、基本的な開発補助として ブラウザ版の生成AI を使用しています。

開発初期は、設計意図や実装判断を自分自身で行うことを重視し、
いわゆるエディタ統合型AI（コード補完・自動生成を常時行うAI）の利用は想定していませんでした。

しかしながら、**UNIX 哲学に基づく「まずは動くものを作る」方針を優先し**、
タスク5「UIスタブ作成」以降は試験的に GitHub Copilot Pro を導入しています。

これは本プロジェクトが、**日常業務では触れる機会の少ない工程・技術領域を重点的に学習すること**を目的の一つとしているためです
（実務では主に Laravel + MySQL を使用）。

### 学習対象の工程
- 要件定義・スコープ整理
- 設計（DB設計・API設計・アーキテクチャ設計）
- 開発環境構築・CI整備
- デプロイや運用を見据えた構成検討

### 学習対象の技術
- Python / FastAPI を用いたバックエンド設計・実装
- PostgreSQL を用いた RDB 設計・運用
- 将来的なフロントエンド分離を見据えた React 連携前提の API 設計
- AI コーディングエディタ（GitHub Copilot）を活用した開発フローの検証・実践
  - 生成コードの妥当性検証
  - 設計意図を踏まえた取捨選択
  - 人間主導での最終判断・実装

AIはあくまで「思考整理・壁打ち・理解補助」の役割に限定し、
**試行錯誤や設計判断そのものは人間が行う**ことを重視しています。
