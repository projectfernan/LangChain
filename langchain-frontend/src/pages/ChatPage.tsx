import { useState, useRef, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'
import ChatBox from '@/components/ChatBox'
import MessageInput from '@/components/MessageInput'
import { streamMessage } from '@/services/chatService'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Message } from '@/types'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const sessionId = useRef(uuidv4())
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text: string) => {
    if (!text.trim() || isStreaming) return

    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: text,
      tools: [],
    }

    const assistantId = uuidv4()
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      tools: [],
      isStreaming: true,
    }

    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setIsStreaming(true)

    const detectedTools: string[] = []

    await streamMessage(
      sessionId.current,
      text,
      (chunk) => {
        // Detect tool usage from stream
        const toolMatch = chunk.match(/\[Using tool: (.+?)\.\.\.\]/)
        if (toolMatch) {
          const toolName = toolMatch[1]
          if (!detectedTools.includes(toolName)) {
            detectedTools.push(toolName)
          }
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, tools: [...detectedTools] } : m
            )
          )
          return
        }

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + chunk } : m
          )
        )
      },
      () => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, isStreaming: false } : m
          )
        )
        setIsStreaming(false)
      },
      (error) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: `Error: ${error}`, isStreaming: false }
              : m
          )
        )
        setIsStreaming(false)
      }
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <p className="text-xs text-muted-foreground">
          Session: {sessionId.current.slice(0, 8)}...
        </p>
      </div>

      <ScrollArea className="flex-1 px-4 pt-4">
        <ChatBox messages={messages} />
        <div ref={bottomRef} />
      </ScrollArea>

      <div className="p-4 border-t">
        <MessageInput onSend={handleSend} disabled={isStreaming} />
      </div>
    </div>
  )
}
