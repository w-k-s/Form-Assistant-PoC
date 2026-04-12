import { apiFetch } from './client'

export interface Thread {
  id: string
  title: string
  created_at: string
}

export interface Message {
  id: string
  thread_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ThreadWithMessages extends Thread {
  messages: Message[]
}

export async function listThreads(): Promise<Thread[]> {
  return apiFetch<Thread[]>('/api/threads')
}

export async function createThread(): Promise<Thread> {
  return apiFetch<Thread>('/api/threads', { method: 'POST' })
}

export async function getThread(id: string): Promise<ThreadWithMessages> {
  return apiFetch<ThreadWithMessages>(`/api/threads/${id}`)
}

export async function deleteThreads(threadIds: string[]): Promise<void> {
  await apiFetch<void>('/api/threads', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_ids: threadIds }),
  })
}

export async function deleteAllThreads(): Promise<void> {
  await apiFetch<void>('/api/threads/all', { method: 'DELETE' })
}
