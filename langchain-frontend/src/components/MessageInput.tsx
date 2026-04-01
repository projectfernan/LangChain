import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export default function MessageInput({ onSend, disabled, placeholder }: MessageInputProps) {
  const [value, setValue] = useState('')

  const handleSend = () => {
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
  }

  return (
    <div className="flex gap-2">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
          }
        }}
        placeholder={placeholder ?? 'Type a message... (Enter to send)'}
        disabled={disabled}
        className="flex-1"
      />
      <Button onClick={handleSend} disabled={disabled || !value.trim()}>
        {disabled ? 'Sending...' : 'Send'}
      </Button>
    </div>
  )
}
