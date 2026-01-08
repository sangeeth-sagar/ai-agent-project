import React, { createContext, useContext, useState, ReactNode } from 'react';
import { chatApi } from '@/lib/api';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Chat {
  chat_id: string;
  chat_name: string;
  personality: string;
  created_at: string;
  messages?: Message[];
}

interface ChatContextType {
  chats: Chat[];
  currentChat: Chat | null;
  messages: Message[];
  isLoading: boolean;
  isSending: boolean;
  fetchChats: () => Promise<void>;
  selectChat: (chatId: string) => Promise<void>;
  createChat: (name: string, personality: string) => Promise<Chat>;
  deleteChat: (chatId: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  clearCurrentChat: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const fetchChats = async () => {
    try {
      setIsLoading(true);
      const data = await chatApi.getAll();
      setChats(data);
    } catch (error) {
      console.error('Failed to fetch chats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectChat = async (chatId: string) => {
    try {
      setIsLoading(true);
      const data = await chatApi.getById(chatId);
      setCurrentChat(data);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createChat = async (name: string, personality: string): Promise<Chat> => {
    const newChat = await chatApi.create(name, personality);
    await fetchChats();
    return newChat;
  };

  const deleteChat = async (chatId: string) => {
    await chatApi.delete(chatId);
    if (currentChat?.chat_id === chatId) {
      setCurrentChat(null);
      setMessages([]);
    }
    await fetchChats();
  };

  const sendMessage = async (content: string) => {
    if (!currentChat) return;

    // Optimistically add user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      const response = await chatApi.sendMessage(currentChat.chat_id, content);
      // Add AI response
      const aiMessage: Message = {
        id: response.id || `ai-${Date.now()}`,
        role: 'assistant',
        content: response.reply || response.message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    } finally {
      setIsSending(false);
    }
  };

  const clearCurrentChat = () => {
    setCurrentChat(null);
    setMessages([]);
  };

  return (
    <ChatContext.Provider
      value={{
        chats,
        currentChat,
        messages,
        isLoading,
        isSending,
        fetchChats,
        selectChat,
        createChat,
        deleteChat,
        sendMessage,
        clearCurrentChat,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
