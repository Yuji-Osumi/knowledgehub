.PHONY: help \
				up up-log down restart logs ps build \
        backend db psql migrate revision \
				health1 health2 health3 health4 health-all

# =========================
# 基本操作
# =========================

help:
	@echo "=====================Usage=====================:"
	@echo "docker:"
	@echo "  make up        - コンテナ起動"
	@echo "  make up-log    - コンテナ起動（ログあり）"
	@echo "  make down      - コンテナ停止"
	@echo "  make restart   - 再起動"
	@echo "  make ps        - 起動状態確認"
	@echo "  make logs      - ログ表示"
	@echo ""
	@echo "DB / Migration:"
	@echo "  make psql             - DB(psql)接続"
	@echo "  make migrate          - alembic upgrade head"
	@echo "  make revision msg=\"\"  - alembic revision (手動)"
	@echo ""
	@echo "health check:"
	@echo "  health-all     - API一括チェック"
	@echo ""

# =========================
# Docker Compose 操作
# =========================

up:
	docker compose up -d

# ログを画面に出しながら起動
up-log:
	docker compose up

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

# すべてのヘルスチェックを順番に実行 DEBUG=Falseの場合はhealth3でエラーが出ます
health-all: health1 health2 health3 health4

health1:
	@echo "--- [1/4] Basic Health Check ---"
	curl http://localhost:8000/api/health
	@echo "\n"

health2:
	@echo "--- [2/4] Client Error Test (400系) ---"
	curl http://localhost:8000/api/error-test
	@echo "\n"

health3:
	@echo "--- [3/4] Server Error Test (500系) ---"
	curl http://localhost:8000/api/error-test-500
	@echo "\n"

health4:
	@echo "--- [4/4] Database Connection Check ---"
	curl http://localhost:8000/api/db-check
	@echo "\n"
