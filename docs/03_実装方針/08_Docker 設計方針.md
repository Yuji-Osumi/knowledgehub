# Docker 設計方針（KnowledgeHub）

## 目的

本ドキュメントは、KnowledgeHub における Docker / Docker Compose の設計意図を明確化し、
「なぜこの構成になっているのか」を将来の自分・第三者が理解できるようにすることを目的とする。

---

## 採用方針（結論）

* Docker は **開発体験の安定化と再現性確保** のために導入
* 本番構成を過度に意識せず、まずは **理解できる最小構成** を優先
* Backend 単体から始め、将来的な拡張（DB / Frontend）を妨げない設計

---

## Dockerfile の責務

Dockerfile は以下のみを責務とする。

* Python / FastAPI 実行環境の定義
* アプリケーション起動コマンドの明示

### ポイント

* `WORKDIR /app` により実行基準点を固定
* アプリケーションは `app.main:app` として起動
* 設定値や環境差分は **Dockerfile に書かない**

👉 Dockerfile = **実行仕様書**

---

## docker-compose.yml の責務

Docker Compose は以下を担う。

* コンテナの起動定義
* 環境変数の注入
* 開発時の利便性向上（volume / port）

### compose をルートに置く理由

```text
knowledgehub/
├── docker-compose.yml
├── backend/
└── frontend（将来）
```

* プロジェクト全体の構成を俯瞰できる
* 将来的に複数サービスを束ねやすい
* infra 的な責務を 1 箇所に集約

---

## env_file を docker-compose に書く理由

* `.env` は **実行環境依存の情報**
* Dockerfile に含めるとイメージが汚染される
* compose によって「どの環境変数が必要か」が明示される

👉 **設定と実行の分離**

---

## volumes を使っている理由（開発用）

```yaml
volumes:
  - ./backend/app:/app/app
```

### 目的

* ソースコード変更を即時反映（ホットリロード）
* イメージ再ビルド回数を減らす

### 補足

* 本番構成では volumes を使わない想定
* dev / prod で compose を分ける余地あり

---

## DB をコンテナ分離していない理由（現時点）

* Docker / Compose 理解を段階的に進めるため
* SQLAlchemy / Alembic 検証を優先

👉 PostgreSQL コンテナは **次フェーズで導入予定**

---

## この設計で得られたこと

* Docker を「おまじない」にせず説明できる
* 実行環境差分によるトラブルを最小化
* 将来的な構成変更に耐えられる土台

---

## 今後の拡張予定

* PostgreSQL コンテナ追加
* dev / prod 用 compose 分離
* CI での Docker build 実行
