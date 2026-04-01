import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Message } from '@/types'

const TOOL_COLORS: Record<string, string> = {
  search_web: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  calculator: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  read_file: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
  get_current_datetime: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
}

const TOOL_ICONS: Record<string, string> = {
  search_web: '🔍',
  calculator: '🧮',
  read_file: '📁',
  get_current_datetime: '🕐',
}

interface ChatBoxProps {
  messages: Message[]
}

export default function ChatBox({ messages }: ChatBoxProps) {
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <p className="text-muted-foreground text-sm">Start a conversation...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 pb-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={cn(
            'flex flex-col gap-1 max-w-[80%]',
            msg.role === 'user' ? 'self-end items-end' : 'self-start items-start'
          )}
        >
          {msg.tools.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {msg.tools.map((tool) => (
                <Badge
                  key={tool}
                  className={cn('text-xs', TOOL_COLORS[tool] ?? 'bg-gray-100 text-gray-700')}
                >
                  {TOOL_ICONS[tool] ?? '🔧'} {tool}
                </Badge>
              ))}
            </div>
          )}

          <div
            className={cn(
              'rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap break-words',
              msg.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-foreground'
            )}
          >
            {msg.content}
            {msg.isStreaming && (
              <span className="inline-block w-1 h-4 ml-1 bg-current animate-pulse rounded-sm" />
            )}
          </div>

          <span className="text-xs text-muted-foreground px-1">
            {msg.role === 'user' ? 'You' : 'AI'}
          </span>
        </div>
      ))}
    </div>
  )
}
