import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ChatPage from '@/pages/ChatPage'
import RagPage from '@/pages/RagPage'

function Nav() {
  const navigate = useNavigate()
  const location = useLocation()
  const active = location.pathname === '/rag' ? 'rag' : 'chat'

  return (
    <nav className="border-b px-4 py-3 flex items-center justify-between bg-background">
      <span className="font-semibold text-lg">🦜 LangChain Demo</span>
      <Tabs value={active}>
        <TabsList>
          <TabsTrigger value="chat" onClick={() => navigate('/')}>
            💬 Chat
          </TabsTrigger>
          <TabsTrigger value="rag" onClick={() => navigate('/rag')}>
            📄 RAG
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="h-screen flex flex-col">
        <Nav />
        <div className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/rag" element={<RagPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}
