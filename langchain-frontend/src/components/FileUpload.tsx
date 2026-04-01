import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  onUpload: (file: File) => void
  isLoading?: boolean
}

const ALLOWED = ['.txt', '.csv', '.json', '.md', '.py', '.pdf']

export default function FileUpload({ onUpload, isLoading }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = (file: File) => {
    const ext = '.' + (file.name.split('.').pop()?.toLowerCase() ?? '')
    if (!ALLOWED.includes(ext)) {
      alert(`Unsupported file type. Allowed: ${ALLOWED.join(', ')}`)
      return
    }
    onUpload(file)
  }

  return (
    <div
      role="button"
      tabIndex={0}
      className={cn(
        'border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer',
        dragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
      )}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        const file = e.dataTransfer.files[0]
        if (file) handleFile(file)
      }}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={ALLOWED.join(',')}
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) handleFile(file)
        }}
      />
      <p className="text-sm text-muted-foreground">
        {isLoading ? '⏳ Uploading & processing document...' : '📂 Drag & drop or click to upload'}
      </p>
      <p className="text-xs text-muted-foreground mt-1">
        Supported: {ALLOWED.join(', ')}
      </p>
      <Button
        variant="outline"
        size="sm"
        className="mt-3"
        disabled={isLoading}
        onClick={(e) => { e.stopPropagation(); inputRef.current?.click() }}
      >
        {isLoading ? 'Processing...' : 'Choose File'}
      </Button>
    </div>
  )
}
