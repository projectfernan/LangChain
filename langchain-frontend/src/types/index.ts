export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  tools: string[]
  isStreaming?: boolean
}

export interface RagUploadResponse {
  filename: string
  chunks: number
  message: string
}

export interface RagChatResponse {
  reply: string
  sources: string[]
}

export interface ChatResponse {
  reply: string
}
