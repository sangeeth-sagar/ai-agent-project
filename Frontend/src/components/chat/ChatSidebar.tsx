import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useChat, Chat } from '@/contexts/ChatContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Plus, Search, LogOut, MoreVertical, Trash2, MessageSquare } from 'lucide-react';
import { NewChatModal } from './NewChatModal';

export function ChatSidebar() {
  const { user, logout } = useAuth();
  const { chats, currentChat, fetchChats, selectChat, deleteChat } = useChat();
  const [searchQuery, setSearchQuery] = useState('');
  const [isNewChatOpen, setIsNewChatOpen] = useState(false);

  useEffect(() => {
    fetchChats();
  }, []);

  const filteredChats = chats.filter((chat) =>
    chat.chat_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleDeleteChat = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteChat(chatId);
  };

  return (
    <div className="w-72 h-screen bg-sidebar flex flex-col border-r border-sidebar-border">
      {/* User Profile Section */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <Popover>
            <PopoverTrigger asChild>
              <button className="flex items-center gap-3 hover:bg-sidebar-accent rounded-lg p-2 transition-colors">
                <div className="w-10 h-10 rounded-full bg-accent flex items-center justify-center text-accent-foreground font-semibold">
                  {user ? getInitials(user.username) : 'U'}
                </div>
                <span className="text-sidebar-foreground font-medium truncate max-w-[120px]">
                  {user?.username}
                </span>
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-64" side="right" align="start">
              <div className="space-y-2">
                <p className="font-medium">{user?.username}</p>
                <p className="text-sm text-muted-foreground">{user?.email}</p>
              </div>
            </PopoverContent>
          </Popover>
          <Button
            variant="ghost"
            size="icon"
            onClick={logout}
            className="text-sidebar-foreground hover:bg-sidebar-accent"
          >
            <LogOut className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <Button
          onClick={() => setIsNewChatOpen(true)}
          className="w-full bg-accent hover:bg-accent/90 text-accent-foreground"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Search */}
      <div className="px-4 pb-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-sidebar-foreground/50" />
          <Input
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-sidebar-accent border-sidebar-border text-sidebar-foreground placeholder:text-sidebar-foreground/50"
          />
        </div>
      </div>

      {/* Chat List */}
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-1 py-2">
          {filteredChats.length === 0 ? (
            <p className="text-center text-sidebar-foreground/50 py-8 text-sm">
              No chats yet
            </p>
          ) : (
            filteredChats.map((chat) => (
              <div
                key={chat.chat_id}
                onClick={() => selectChat(chat.chat_id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                  currentChat?.chat_id === chat.chat_id
                    ? 'bg-sidebar-accent'
                    : 'hover:bg-sidebar-accent/50'
                }`}
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <MessageSquare className="w-4 h-4 text-sidebar-foreground/70 flex-shrink-0" />
                  <span className="text-sidebar-foreground truncate text-sm">
                    {chat.chat_name}
                  </span>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-sidebar-border rounded transition-opacity"
                    >
                      <MoreVertical className="w-4 h-4 text-sidebar-foreground/70" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={(e) => handleDeleteChat(chat.chat_id, e as any)}
                      className="text-destructive focus:text-destructive"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      <NewChatModal open={isNewChatOpen} onOpenChange={setIsNewChatOpen} />
    </div>
  );
}
