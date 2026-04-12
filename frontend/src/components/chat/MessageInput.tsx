import { useState, useRef, useEffect } from 'react'

interface Props {
  disabled: boolean
  onSubmit: (content: string) => void
}

export default function MessageInput({ disabled, onSubmit }: Props) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!disabled) textareaRef.current?.focus()
  }, [disabled])

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    const trimmed = message.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setMessage('')
  }

  return (
    <div className="border-t border-border p-4 bg-card">
      <form
        onSubmit={(e) => { e.preventDefault(); submit() }}
        className="flex gap-2 items-end"
      >
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message..."
            rows={1}
            disabled={disabled}
            className="w-full resize-none rounded-lg border border-input bg-background px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring min-h-[42px] max-h-40 overflow-y-auto disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {disabled ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </form>
      <p className="text-xs text-muted-foreground mt-2">Press Enter to send, Shift+Enter for new line</p>
    </div>
  )
}
