# セキュリティ方針（MVP）

## 目的

本ドキュメントは、KnowledgeHub における **最低限のセキュリティ方針**を定める。

MVP 前提のため、
網羅的な対策ではなく **事故を防ぐための基本方針**に限定する。

---

## 基本スタンス

* セキュリティは「完璧」より「一貫性」
* フレームワーク標準を信頼する
* 必要になった時点で強化する

---

## 認証・セッション管理

### 方針

* **JWT + Cookie 認証を採用する**
* JWT を HttpOnly Cookie に保存する
* トークンを LocalStorage に保存しない（XSS 対策）
* ステートレス設計（JWT 署名検証）
* トークン無効化は Redis ブラックリスト方式

---

### JWT 設計

#### **トークン構造**
```json
{
  "user_id": "uuid-string",
  "exp": 1234567890,
  "jti": "unique-token-id"
}
```

#### **署名アルゴリズム**
- HS256（HMAC-SHA256）
- シークレットキー：64 バイト以上の暗号学的乱数

#### **有効期限**
- MVP：24 時間固定
- Phase 2：1 時間（リフレッシュトークン併用）

---

### Cookie 設定方針

* HttpOnly：有効（JavaScript からアクセス不可）
* Secure：本番では有効（HTTPS のみ）
* SameSite：Lax（CSRF 対策）
* Max-Age：86400 秒（24 時間）

👉 CSRF 対策は **SameSite による軽減**を前提とする

---

### トークン検証フロー

```
1. Cookie から JWT 取得
2. JWT 署名検証（SECRET_KEY）
3. 有効期限チェック（exp）
4. ブラックリスト確認（Redis: blacklist:{jti}）
5. user_id を抽出して処理継続
```

---

### トークン無効化（ブラックリスト）

#### **実装方針**
- ログアウト時に Redis にトークン ID（jti）を保存
- キー構造：`blacklist:{jti}` → `"true"`
- TTL：24 時間（トークン有効期限と同じ）

#### **検証時の処理**
```python
if redis.get(f"blacklist:{jti}"):
    raise 401  # トークン無効
```

#### **対象ケース**
- ユーザーの明示的なログアウト
- セキュリティインシデント時の強制無効化（手動）

---

### JWT シークレットキー管理

#### **生成方法**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### **保存場所**
- 開発環境：`.env` ファイル（Git 管理外）
- 本番環境：Railway 環境変数

#### **要件**
- 長さ：64 バイト以上
- エントロピー：暗号学的に安全な乱数生成器
- 本番と開発で異なるキーを使用

#### **ローテーション**
- MVP：漏洩時のみ手動ローテーション
- Phase 2：グレースピリオド実装（24h 猶予）

---

### パスワード管理

* bcrypt によるハッシュ化
* ストレッチング回数：デフォルト（12 rounds）
* パスワードは平文で保存しない
* パスワードはログに出力しない

---

## CSRF 対策

* SameSite=Lax を基本とする
* 明示的な CSRF トークンは MVP では導入しない
* 状態変更系 API は POST / PUT / DELETE のみに限定する

---

## XSS 対策

* React の自動エスケープを信頼する
* `dangerouslySetInnerHTML` は原則禁止
* ユーザー入力をそのまま HTML として保存しない

---

### パスワード管理

* bcrypt によるハッシュ化
* ストレッチング回数：12 rounds（デフォルト）
* パスワードは平文で保存しない
* パスワードはログに出力しない

**bcrypt 選定理由：**
- ✅ 暗号学的に安全（salt 自動付与）
- ✅ ストレッチング（遅いハッシュ）でブルートフォース耐性
- ✅ Python `passlib` で簡単実装
- ✅ パスワード更新時の互換性維持

**実装例：**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# パスワードハッシュ化
hashed_password = pwd_context.hash("user_password")

# パスワード検証
pwd_context.verify("user_password", hashed_password)  # True/False
```

---

## SQL Injection 対策

* ORM（SQLAlchemy）を基本とする
* 生 SQL は最小限・理由必須
* パラメータバインドを必ず使用する

---

## 入力バリデーション

* Backend 側で必ず検証する
* Pydantic による validation を利用する
* Frontend の検証は UX 改善目的のみ

---

## Secret 管理

* Secret はコードに書かない
* Railway の環境変数で管理する

例：

* DATABASE_URL
* SECRET_KEY

---

## ログと情報漏洩

* パスワード・トークンはログに出さない
* エラーメッセージに内部情報を含めない

---

## 今回やらないこと（明示）

* レートリミット
* WAF
* 権限の細分化
* 詳細な監査ログ

👉 必要になった段階で追加する

---

## 判断に迷った場合

* フレームワークの標準に乗っているか
* 情報を出しすぎていないか
* MVP として過剰でないか

---

この方針は、
**個人開発における現実的な安全ライン**を示すものである。
