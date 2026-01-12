import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import ArticleList from "./pages/ArticleList"
import ArticleDetail from "./pages/ArticleDetail"
import ArticleEdit from "./pages/ArticleEdit"

function App() {
  return (
    <BrowserRouter>
      <div className="p-6">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/articles" element={<ArticleList />} />
          <Route path="/articles/:id" element={<ArticleDetail />} />
          <Route path="/articles/:id/edit" element={<ArticleEdit />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
