import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getArticleById } from "@/lib/api"
import type { Article } from "@/types"

export default function ArticleDetail() {
  const { publicId } = useParams()
  const [article, setArticle] = useState<Article | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchArticle = async () => {
      if (!publicId) return
      setLoading(true)
      try {
        const data = await getArticleById(publicId)
        setArticle(data)
      } finally {
        setLoading(false)
      }
    }

    fetchArticle()
  }, [publicId])

  if (loading) {
    return <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>
  }

  if (!article) {
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
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{article.title}</h1>
        <div className="space-x-2">
          <button
            className="rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700"
            onClick={() => navigate(`/articles/${article.publicId}/edit`)}
          >
            編集
          </button>
          <button
            className="rounded border border-gray-300 px-3 py-2 text-gray-700 hover:bg-gray-100"
            onClick={() => navigate("/articles")}
          >
            戻る
          </button>
        </div>
      </div>

      <div className="text-sm text-gray-600">
        <span>公開日: {new Date(article.publishedAt).toLocaleString()}</span>
        <span className="ml-3">更新日: {new Date(article.updatedAt).toLocaleString()}</span>
      </div>

      {article.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {article.tags.map(tag => (
            <span key={tag.publicId} className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-700">
              {tag.name}
            </span>
          ))}
        </div>
      )}

      <div className="whitespace-pre-wrap rounded border border-gray-200 p-4 text-sm leading-relaxed">
        {article.content}
      </div>
    </div>
  )
}
