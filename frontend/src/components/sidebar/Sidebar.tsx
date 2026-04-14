import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { listThreads, createThread, deleteThreads, deleteAllThreads, type Thread } from '../../api/threads'
import ThreadItem from './ThreadItem'

interface Props {
  activeThreadId: string | null
}

export default function Sidebar({ activeThreadId }: Props) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isManaging, setIsManaging] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const { data: threads = [] } = useQuery({
    queryKey: ['threads'],
    queryFn: listThreads,
  })

  const { mutate: newThread, isPending } = useMutation({
    mutationFn: createThread,
    onSuccess: (thread: Thread) => {
      queryClient.invalidateQueries({ queryKey: ['threads'] })
      navigate(`/threads/${thread.id}`)
    },
  })

  const { mutate: removeSelected, isPending: isDeletingSelected } = useMutation({
    mutationFn: () => deleteThreads(Array.from(selectedIds)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threads'] })
      if (activeThreadId && selectedIds.has(activeThreadId)) navigate('/')
      setSelectedIds(new Set())
      setIsManaging(false)
    },
  })

  const { mutate: removeAll, isPending: isDeletingAll } = useMutation({
    mutationFn: deleteAllThreads,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['threads'] })
      navigate('/')
      setSelectedIds(new Set())
      setIsManaging(false)
    },
  })

  function toggleManaging() {
    setIsManaging((v) => !v)
    setSelectedIds(new Set())
  }

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function handleDeleteSelected() {
    if (!window.confirm(`Delete ${selectedIds.size} selected chat${selectedIds.size !== 1 ? 's' : ''}?`)) return
    removeSelected()
  }

  function handleDeleteAll() {
    if (!window.confirm(`Delete all ${threads.length} chat${threads.length !== 1 ? 's' : ''}? This cannot be undone.`)) return
    removeAll()
  }

  return (
    <aside className="w-64 border-r border-border bg-card flex flex-col shrink-0 h-full">
      <div className="p-3 border-b border-border flex items-center gap-2">
        <button
          onClick={() => newThread()}
          disabled={isPending}
          className="flex-1 flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New chat
        </button>

        <button
          onClick={toggleManaging}
          title="Manage"
          className={`p-1.5 rounded-md transition-colors ${isManaging ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'}`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {threads.map((thread) => (
          <ThreadItem
            key={thread.id}
            thread={thread}
            isActive={thread.id === activeThreadId}
            onClick={() => navigate(`/threads/${thread.id}`)}
            isManaging={isManaging}
            isSelected={selectedIds.has(thread.id)}
            onToggle={toggleSelect}
          />
        ))}
      </div>

      {isManaging && (
        <div className="p-3 border-t border-border flex flex-col gap-2">
          <button
            onClick={handleDeleteSelected}
            disabled={selectedIds.size === 0 || isDeletingSelected || isDeletingAll}
            className="w-full px-3 py-2 rounded-md text-sm font-medium border border-border bg-secondary text-secondary-foreground hover:bg-accent hover:text-accent-foreground transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Delete selected{selectedIds.size > 0 ? ` (${selectedIds.size})` : ''}
          </button>
          <button
            onClick={handleDeleteAll}
            disabled={threads.length === 0 || isDeletingSelected || isDeletingAll}
            className="w-full px-3 py-2 rounded-md text-sm font-medium bg-destructive text-destructive-foreground hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Delete all
          </button>
        </div>
      )}
    </aside>
  )
}
