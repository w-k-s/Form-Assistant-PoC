import { apiFetch } from './client'
import type { Message } from './threads'

export async function postMessage(threadId: string, content: string): Promise<Message> {
  return apiFetch<Message>(`/api/threads/${threadId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  })
}
