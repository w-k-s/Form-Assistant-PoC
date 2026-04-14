import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/threads/:threadId" element={<ChatPage />} />
          <Route path="/*" element={<ChatPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
