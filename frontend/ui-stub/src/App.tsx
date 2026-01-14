import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import Login from "./pages/Login"
import ArticleList from "./pages/ArticleList"
import ArticleDetail from "./pages/ArticleDetail"
import ArticleFormPage from "./pages/ArticleFormPage"
import Register from "./pages/Register"
import NotFound from "./pages/NotFound"
import { AuthProvider, useAuth } from "./lib/auth"
import type { ReactElement } from "react"

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/articles"
              element={
                <ProtectedRoute>
                  <ArticleList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/articles/new"
              element={
                <ProtectedRoute>
                  <ArticleFormPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/articles/:publicId"
              element={
                <ProtectedRoute>
                  <ArticleDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/articles/:publicId/edit"
              element={
                <ProtectedRoute>
                  <ArticleFormPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

const ProtectedRoute = ({ children }: { children: ReactElement }) => {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return children
}
