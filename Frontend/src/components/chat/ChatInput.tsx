import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send } from 'lucide-react';

export function ChatInput() {
  const [message, setMessage] = useState('');
  const { sendMessage, isSending, currentChat } = useChat();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [message]);

  const handleSubmit = async () => {
    if (!message.trim() || isSending || !currentChat) return;

    const content = message.trim();
    setMessage('');
    await sendMessage(content);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t p-4 bg-background">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3 bg-card rounded-2xl border p-2 shadow-sm">
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 min-h-[44px] max-h-[150px] resize-none border-0 focus-visible:ring-0 bg-transparent"
            rows={1}
            disabled={isSending}
          />
          <Button
            onClick={handleSubmit}
            disabled={!message.trim() || isSending}
            size="icon"
            className="rounded-full bg-accent hover:bg-accent/90 h-10 w-10 flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-xs text-center text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
