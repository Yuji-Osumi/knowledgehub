import { Link } from "react-router-dom"

export default function NotFound() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">404 Not Found</h1>
      <p className="text-sm text-gray-600">ページが見つかりませんでした。</p>
      <Link
        className="inline-block rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        to="/articles"
      >
        一覧へ
      </Link>
    </div>
  )
}
