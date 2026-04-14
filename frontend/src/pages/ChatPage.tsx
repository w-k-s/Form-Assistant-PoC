import { useParams } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Sidebar from '../components/sidebar/Sidebar'
import ChatArea from '../components/chat/ChatArea'

export default function ChatPage() {
  const { threadId } = useParams<{ threadId: string }>()

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeThreadId={threadId ?? null} />
        <main className="flex-1 min-w-0">
          {threadId ? (
            <ChatArea key={threadId} threadId={threadId} />
          ) : (
            <div className="flex h-full items-center justify-center">
              <p className="text-muted-foreground text-sm">Select a thread or create a new chat</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
