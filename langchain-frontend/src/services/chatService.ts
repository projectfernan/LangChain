import api from '@/utils/axiosInstance'
import type { ChatResponse } from '@/types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const sendMessage = async (
  sessionId: string,
  message: string
): Promise<ChatResponse> => {
  const { data } = await api.post<ChatResponse>('/chat', {
    session_id: sessionId,
    message,
  })
  return data
}

export const streamMessage = async (
  sessionId: string,
  message: string,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (error: string) => void
): Promise<void> => {
  try {
    const response = await fetch(`${BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message }),
    })

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    if (!response.body) throw new Error('No response body')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const text = decoder.decode(value)
      const lines = text.split('\n')

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue

        const data = line.slice(6)

        if (data === '[DONE]') {
          onDone()
          return
        }
        if (data.startsWith('[ERROR]')) {
          onError(data.slice(8))
          return
        }
        if (data) {
          onChunk(data.replace(/\\n/g, '\n'))
        }
      }
    }

    onDone()
  } catch (error) {
    onError(error instanceof Error ? error.message : 'Stream failed')
  }
}
