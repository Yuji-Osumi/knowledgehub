.PHONY: help up down restart logs ps build \
        backend db psql migrate revision \
				health

# =========================
# 基本操作
# =========================

help:
	@echo "Usage:"
	@echo "  make up        - コンテナ起動"
	@echo "  make down      - コンテナ停止"
	@echo "  make restart   - 再起動"
	@echo "  make ps        - 起動状態確認"
	@echo "  make logs      - ログ表示"
	@echo ""
	@echo "DB / Migration:"
	@echo "  make psql             - DB(psql)接続"
	@echo "  make migrate          - alembic upgrade head"
	@echo "  make revision msg=""  - alembic revision (手動)"
	@echo "health check:"
	@echo "  health        - APIチェック"

# =========================
# Docker Compose 操作
# =========================

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d

build:
	docker compose up -d --build

ps:
	docker compose ps

logs:
	docker compose logs -f

# =========================
# DB / Alembic
# =========================

backend:
	docker compose exec backend bash

db:
	docker compose exec db bash

# 直接SQLを操作できる状態にする \dtでテーブルを確認　docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
psql:
	docker compose exec db psql -U admin_user -d knowledgehub_db

# データベースの構成を最新化
migrate:
	docker compose exec backend alembic upgrade head

# マイグレーションファイルを作成 例）make revision msg="add user table"
revision:
ifndef msg
	$(error 引数 msg が指定されていません。 例: make revision msg="add_user_table")
endif
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

# =========================
# ヘルスチェック
# =========================

health:
	curl http://localhost:8000/api/health
