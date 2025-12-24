# KnowledgeHub

## 概要
ナレッジ共有・検索を目的とした個人開発プロジェクトです。
バックエンドは FastAPI を用いて REST API を構築しています。

## 技術スタック
- **Language:** Python 3.12
- **Framework:** FastAPI
- **Validation:** Pydantic v2
- **Database:** SQLAlchemy / PostgreSQL (予定)
- **Infrastructure:** Docker / Docker Compose (予定)

## 開発状況
- [x] Python 環境構築
- [x] FastAPI 初期化・起動確認
- [ ] アプリ基盤設定
- [ ] DB 設計・実装
- [ ] API 実装

## 起動方法（Backend）
```bash
# 仮想環境の有効化（Windows）
.venv\Scripts\activate

# サーバー起動
uvicorn app.main:app --reload
```
