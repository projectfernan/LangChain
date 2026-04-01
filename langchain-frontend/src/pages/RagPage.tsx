import { useState, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'
import FileUpload from '@/components/FileUpload'
import ChatBox from '@/components/ChatBox'
import MessageInput from '@/components/MessageInput'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { uploadDocument, ragChat } from '@/services/ragService'
import type { Message } from '@/types'

export default function RagPage() {
  const [uploadedFile, setUploadedFile] = useState<string | null>(null)
  const [chunks, setChunks] = useState<number>(0)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sources, setSources] = useState<string[]>([])
  const sessionId = useRef(uuidv4())

  const handleUpload = async (file: File) => {
    setIsLoading(true)
    try {
      const result = await uploadDocument(file)
      setUploadedFile(result.filename)
      setChunks(result.chunks)
      setMessages([])
      setSources([])
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Upload failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = async (text: string) => {
    if (!text.trim() || !uploadedFile || isLoading) return

    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: text,
      tools: [],
    }

    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)
    setSources([])

    try {
      const result = await ragChat(sessionId.current, uploadedFile, text)

      const assistantMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: result.reply,
        tools: [],
      }

      setMessages((prev) => [...prev, assistantMsg])
      setSources(result.sources)
    } catch (error) {
      const errorMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Something went wrong'}`,
        tools: [],
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Upload Section */}
      <div className="p-4 border-b space-y-3">
        <FileUpload onUpload={handleUpload} isLoading={isLoading} />
        {uploadedFile && (
          <div className="flex items-center gap-2">
            <Badge variant="secondary">📄 {uploadedFile}</Badge>
            <Badge variant="outline">{chunks} chunks indexed</Badge>
          </div>
        )}
      </div>

      {uploadedFile ? (
        <>
          <ScrollArea className="flex-1 px-4 pt-4">
            <ChatBox messages={messages} />
            {isLoading && (
              <div className="flex gap-1 p-3 self-start">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.15s]" />
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.3s]" />
              </div>
            )}
          </ScrollArea>

          {/* Sources */}
          {sources.length > 0 && (
            <div className="px-4 py-2 border-t space-y-1">
              <p className="text-xs font-medium text-muted-foreground">
                📌 Sources used ({sources.length} chunks):
              </p>
              <div className="flex flex-col gap-1 max-h-28 overflow-y-auto">
                {sources.map((src, i) => (
                  <div key={i} className="text-xs text-muted-foreground bg-muted rounded px-2 py-1 line-clamp-2">
                    {src}
                  </div>
                ))}
              </div>
              <Separator />
            </div>
          )}

          <div className="p-4 border-t">
            <MessageInput
              onSend={handleSend}
              disabled={isLoading}
              placeholder="Ask a question about your document..."
            />
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground text-sm">
            Upload a document above to start asking questions
          </p>
        </div>
      )}
    </div>
  )
}
