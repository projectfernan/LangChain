import api from '@/utils/axiosInstance'
import type { RagUploadResponse, RagChatResponse } from '@/types'

export const uploadDocument = async (file: File): Promise<RagUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post<RagUploadResponse>('/rag/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const ragChat = async (
  sessionId: string,
  filename: string,
  message: string
): Promise<RagChatResponse> => {
  const { data } = await api.post<RagChatResponse>('/rag/chat', {
    session_id: sessionId,
    filename,
    message,
  })
  return data
}
