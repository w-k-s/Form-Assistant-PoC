import { cn } from '../../lib/utils'
import type { Thread } from '../../api/threads'

interface Props {
  thread: Thread
  isActive: boolean
  onClick: () => void
  isManaging?: boolean
  isSelected?: boolean
  onToggle?: (id: string) => void
}

export default function ThreadItem({ thread, isActive, onClick, isManaging, isSelected, onToggle }: Props) {
  if (isManaging) {
    return (
      <label className={cn(
        'w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm truncate transition-colors cursor-pointer',
        isSelected
          ? 'bg-accent text-accent-foreground'
          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
      )}>
        <input
          type="checkbox"
          checked={isSelected}
          onChange={() => onToggle?.(thread.id)}
          className="shrink-0 accent-primary"
        />
        <span className="truncate">{thread.title}</span>
      </label>
    )
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left px-3 py-2 rounded-md text-sm truncate transition-colors',
        isActive
          ? 'bg-accent text-accent-foreground font-medium'
          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
      )}
    >
      {thread.title}
    </button>
  )
}
