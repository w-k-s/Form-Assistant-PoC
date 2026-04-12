import { useState, useRef, useCallback } from 'react'

interface UseStreamOptions {
  onDone: (fullContent: string) => void
}

export function useStream({ onDone }: UseStreamOptions) {
  const [streamingContent, setStreamingContent] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const esRef = useRef<EventSource | null>(null)

  const startStream = useCallback((threadId: string) => {
    // Close any existing stream
    esRef.current?.close()

    setStreamingContent('')
    setIsStreaming(true)

    const es = new EventSource(`/api/threads/${threadId}/stream`)
    esRef.current = es

    let accumulated = ''

    es.addEventListener('token', (e) => {
      accumulated += e.data
      setStreamingContent(accumulated)
    })

    es.addEventListener('done', () => {
      es.close()
      esRef.current = null
      setIsStreaming(false)
      setStreamingContent('')
      onDone(accumulated)
    })

    es.onerror = () => {
      es.close()
      esRef.current = null
      setIsStreaming(false)
      if (accumulated) {
        setStreamingContent('')
        onDone(accumulated)
      }
    }
  }, [onDone])

  const cancel = useCallback(() => {
    esRef.current?.close()
    esRef.current = null
    setIsStreaming(false)
    setStreamingContent('')
  }, [])

  return { streamingContent, isStreaming, startStream, cancel }
}
