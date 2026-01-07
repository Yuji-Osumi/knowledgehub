# Alembic マイグレーション設計（KnowledgeHub）

## 目的

本ドキュメントは、KnowledgeHub における **Alembic マイグレーション運用の設計方針** を整理し、
将来の自分や第三者が「どのように DB スキーマを変更・管理するのか」を迷わず理解できるようにすることを目的とする。

最低限のルールと考え方を定義する。

---

## Alembic の役割

Alembic は **DB スキーマ変更の履歴をコードとして管理するためのツール** である。

* DB を直接操作せず、必ずマイグレーション経由で変更する
* スキーマ変更履歴を Git 管理できる
* SQLAlchemy の models と DB 構造の乖離を防ぐ

```text
models の変更
   ↓
alembic revision
   ↓
alembic upgrade
   ↓
DB スキーマが更新される
```

Alembic は **Git における commit / checkout のような存在** と捉える。

---

## 運用方針（基本ルール）

### スキーマ変更ルール

* DB スキーマ変更は **必ず Alembic を通す**
* DB に対する手動の ALTER / DROP は行わない
* models を変更したら revision を作成する
* upgrade は原則 `head` のみを使用する

---

## 採用コマンドセット

日常的に使用するコマンドは以下に限定する。

```bash
make revision msg="add users table"
make migrate
```

* `revision`：変更内容を migration ファイルとして記録
* `migrate`：DB を最新スキーマへ反映

👉 コマンドを固定することで、運用のブレを防ぐ

---

## autogenerate の方針

### 結論

**autogenerate を基本方針として採用する**。

### 理由

* 個人開発・小規模構成である
* models と DB の差分検知を自動化できる
* マイグレーション作成コストを下げられる

### 注意点

* migration ファイルは **必ず中身をレビューする**
* 意図しない DROP / RENAME / COLUMN 削除がないか確認する

👉 **自動生成 + 人間レビュー** を前提とする

---

## revision ファイルの粒度ルール

* 1 機能 = 1 revision を基本とする
* 意味のある単位で分割する

### 良い例

```text
add_users_table
add_articles_table
add_article_tags_table
```

### 悪い例

```text
update_models
fix_tables
```

👉 「あとから見て内容が分かるか」を基準に命名する

---

## 開発中の失敗に対する考え方

### ローカル開発環境では

* DB は壊してもよい
* volume 削除 → 再作成 → `alembic upgrade head` で復旧可能

migration が壊れた場合も、
**データ保全より構造理解を優先** する。

※ 本番環境のデータ移行は本フェーズでは考慮しない
