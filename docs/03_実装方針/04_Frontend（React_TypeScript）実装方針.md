# Frontend（React / TypeScript）実装方針

## 目的

本ドキュメントは、KnowledgeHub Frontend における **React / TypeScript 実装の判断基準**を定める。

Backend 同様、MVP 前提で
「最小 → 動く → 整える」を最優先とする。

---

## 採用技術

* Vite
* React
* TypeScript
* Tailwind CSS
* Tiptap Editor

---

## ディレクトリ構成方針

### 初期（MVP開始時）

```txt
frontend/
└─ src/
   ├─ pages/
   ├─ components/
   ├─ hooks/
   ├─ lib/
   └─ main.tsx
```

* pages：ルーティング単位
* components：再利用 UI
* hooks：カスタム hooks
* lib：API / utility

---

### 分割を検討するタイミング

* components が 15 個を超えた
* 同名コンポーネントが増えた
* ファイルが 300 行を超えた

👉 先に **フォルダを切らず、ファイル分割を優先**

---

## コンポーネント設計

* 関数コンポーネントのみ使用
* 1 コンポーネント 1 責務

```tsx
function NoteList() {
  return <div />
}
```

---

## State 管理

* 基本は useState / useEffect
* グローバル state は最小限

❌ Redux / Zustand は MVP では使わない

---

## API 通信方針

* API 呼び出しは lib/api に集約
* components 内で直接 fetch しない

```ts
export async function fetchNotes() {
  const res = await fetch('/api/notes')
  return res.json()
}
```

---

## TypeScript 方針

* any は原則禁止
* 型は API Response に合わせる
* union / generics は最小限

---

## スタイリング（Tailwind）

* className は書きすぎない
* 共通 UI は component 化する

```tsx
<button className="px-4 py-2 rounded">Save</button>
```

---

## Editor（Tiptap）

* 表示・編集責務を分離する
* 拡張は必要になった時のみ追加

---

## lint / フォーマット

* ESLint：必須
* Prettier：必須

---

## 禁止事項（Frontend）

* 巨大コンポーネント（500 行超）
* JSX 内での複雑なロジック
* 型定義のコピペ量産
* 理由のない state のグローバル化

---

## 判断に迷った場合

* それは MVP に必要か
* 将来消しやすいか
* 読み返して理解できるか

---

この方針は、
**迷わず UI 実装を進めるためのガイド**である。
