import { useState } from 'react'
import Navbar from '../components/layout/Navbar'
import Sidebar from '../components/sidebar/Sidebar'
import ChatArea from '../components/chat/ChatArea'

export default function ChatPage() {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null)

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeThreadId={activeThreadId} onSelectThread={setActiveThreadId} />
        <main className="flex-1 min-w-0">
          {activeThreadId ? (
            <ChatArea key={activeThreadId} threadId={activeThreadId} />
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
