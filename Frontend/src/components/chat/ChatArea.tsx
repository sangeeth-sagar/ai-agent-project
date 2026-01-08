import { useRef, useEffect } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { Bot, MessageSquarePlus } from 'lucide-react';

export function ChatArea() {
  const { currentChat, messages, isSending } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  if (!currentChat) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-background p-8">
        <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center mb-6">
          <Bot className="w-12 h-12 text-primary" />
        </div>
        <h2 className="text-2xl font-semibold text-foreground mb-2">Welcome to AI Chat</h2>
        <p className="text-muted-foreground text-center max-w-md mb-6">
          Start a new conversation or select an existing chat from the sidebar to begin.
        </p>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MessageSquarePlus className="w-4 h-4" />
          <span>Click "New Chat" to get started</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen bg-background">
      {/* Chat Header */}
      <div className="h-16 border-b flex items-center px-6">
        <h1 className="text-lg font-semibold text-foreground">{currentChat.chat_name}</h1>
        <span className="ml-3 text-xs px-2 py-1 rounded-full bg-secondary text-secondary-foreground capitalize">
          {/* --- FIX IS HERE --- 
              1. Use 'mode' instead of 'personality'
              2. Add a fallback || 'general' so it never crashes even if data is missing 
          */}
          {(currentChat.mode || 'general').replace('_', ' ')}
        </span>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No messages yet. Start the conversation!
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              // Use index as key to avoid "undefined key" warnings
              <MessageBubble key={index} message={message} />
            ))
          )}
          {isSending && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-accent animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-accent animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-accent animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-sm">AI is typing...</span>
            </div>
          )}
          {/* Invisible div to scroll to */}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <ChatInput />
    </div>
  );
}