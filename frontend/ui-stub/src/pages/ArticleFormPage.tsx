import { useEffect, useMemo, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getArticleById, saveArticle } from "@/lib/api"
import type { Article } from "@/types"

export default function ArticleFormPage() {
  const { publicId } = useParams()
  const isNew = !publicId
  const [article, setArticle] = useState<Article | null>(null)
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")
  const [loading, setLoading] = useState(!isNew)
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchArticle = async () => {
      if (isNew || !publicId) return
      setLoading(true)
      try {
        const data = await getArticleById(publicId)
        setArticle(data)
        if (data) {
          setTitle(data.title)
          setContent(data.content)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchArticle()
  }, [isNew, publicId])

  const heading = useMemo(() => (isNew ? "新規記事" : "記事を編集"), [isNew])

  const handleSave = async () => {
    setSaving(true)
    try {
      const now = new Date().toISOString()
      const base: Article = isNew
        ? {
          publicId: `uuid-temp-${Date.now()}`,
          title: title || "無題の記事",
          content,
          tags: [],
          isPublished: false,
          publishedAt: now,
          folderId: null,
          createdAt: now,
          updatedAt: now,
        }
        : {
          ...(article as Article),
          title,
          content,
          updatedAt: now,
        }

      await saveArticle(base)
      navigate(isNew ? "/articles" : `/articles/${base.publicId}`)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>
  }

  if (!isNew && !article) {
    return (
      <div className="space-y-4">
        <div className="p-4 border border-red-200 bg-red-50 text-red-800">記事が見つかりません。</div>
        <button
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          onClick={() => navigate("/articles")}
        >
          一覧へ戻る
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">{heading}</h1>

      <div className="space-y-2">
        <label className="block text-sm font-medium">タイトル</label>
        <input
          className="w-full rounded border border-gray-300 px-3 py-2"
          value={title}
          onChange={e => setTitle(e.target.value)}
          disabled={saving}
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">本文</label>
        <textarea
          className="w-full rounded border border-gray-300 px-3 py-2"
          rows={10}
          value={content}
          onChange={e => setContent(e.target.value)}
          disabled={saving}
        />
      </div>

      <div className="flex gap-3">
        <button
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-60"
          onClick={handleSave}
          disabled={saving}
        >
          保存
        </button>
        <button
          className="rounded border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-100"
          onClick={() => navigate("/articles")}
          disabled={saving}
        >
          キャンセル
        </button>
      </div>

      {saving && <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>}
    </div>
  )
}
