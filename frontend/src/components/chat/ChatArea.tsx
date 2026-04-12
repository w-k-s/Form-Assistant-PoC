import { useEffect, useRef, useCallback } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getThread, type Message } from '../../api/threads'
import { postMessage } from '../../api/messages'
import { useStream } from '../../hooks/useStream'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import MessageInput from './MessageInput'

interface Props {
  threadId: string
}

export default function ChatArea({ threadId }: Props) {
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: thread } = useQuery({
    queryKey: ['thread', threadId],
    queryFn: () => getThread(threadId),
    enabled: !!threadId,
  })

  // Local optimistic messages appended before server confirms
  const localMessages = useRef<Message[]>([])
  const messages: Message[] = [
    ...(thread?.messages ?? []),
    ...localMessages.current.filter(
      (lm) => !(thread?.messages ?? []).some((m) => m.id === lm.id),
    ),
  ]

  const { streamingContent, isStreaming, startStream } = useStream({
    onDone: (fullContent) => {
      localMessages.current = []
      queryClient.invalidateQueries({ queryKey: ['thread', threadId] })
      queryClient.invalidateQueries({ queryKey: ['threads'] })
      // Suppress unused warning — fullContent is used implicitly via invalidation
      void fullContent
    },
  })

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, streamingContent])

  const handleSubmit = useCallback(async (content: string) => {
    const optimistic: Message = {
      id: `opt-${Date.now()}`,
      thread_id: threadId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    localMessages.current = [optimistic]

    try {
      await postMessage(threadId, content)
      startStream(threadId)
    } catch (err) {
      localMessages.current = []
      console.error(err)
    }
  }, [threadId, startStream])

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-muted-foreground text-sm">Start a conversation</p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isStreaming && streamingContent && (
              <MessageBubble message={{ role: 'assistant', content: streamingContent }} />
            )}
            {isStreaming && !streamingContent && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <MessageInput disabled={isStreaming} onSubmit={handleSubmit} />
    </div>
  )
}
