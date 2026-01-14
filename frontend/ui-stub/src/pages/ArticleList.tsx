import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getArticles } from "@/lib/api"
import { useAuth } from "@/lib/auth"
import type { Article } from "@/types"

export default function ArticleList() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { logout } = useAuth()

  useEffect(() => {
    const fetchArticles = async () => {
      setLoading(true)
      try {
        const data = await getArticles()
        setArticles(data)
      } finally {
        setLoading(false)
      }
    }

    fetchArticles()
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Articles</h1>
        <div className="flex items-center gap-2">
          <button
            className="rounded border border-gray-300 px-3 py-2 text-gray-700 hover:bg-gray-100"
            onClick={() => logout()}
          >
            ログアウト
          </button>
          <button
            className="rounded bg-green-600 px-3 py-2 text-white hover:bg-green-700"
            onClick={() => navigate("/articles/new")}
          >
            新規作成
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-4 border border-gray-300 text-sm">読み込み中...</div>
      ) : (
        <ul className="space-y-3">
          {articles.map(article => (
            <li
              key={article.publicId}
              className="cursor-pointer rounded border border-gray-200 p-4 shadow-sm hover:shadow"
              onClick={() => navigate(`/articles/${article.publicId}`)}
            >
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium">{article.title}</h2>
                <span className="text-xs text-gray-500">更新 {new Date(article.updatedAt).toLocaleString()}</span>
              </div>
              {article.tags.length > 0 && (
                <p className="mt-2 text-sm text-gray-600">
                  タグ: {article.tags.map(tag => tag.name).join(", ")}
                </p>
              )}
              {!article.isPublished && (
                <span className="mt-2 inline-block rounded bg-yellow-100 px-2 py-1 text-xs text-yellow-800">下書き</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
