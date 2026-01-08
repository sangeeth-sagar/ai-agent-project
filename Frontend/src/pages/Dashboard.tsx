import { ChatProvider } from '@/contexts/ChatContext';
import { ChatSidebar } from '@/components/chat/ChatSidebar';
import { ChatArea } from '@/components/chat/ChatArea';

export default function Dashboard() {
  return (
    <ChatProvider>
      <div className="flex h-screen w-full">
        <ChatSidebar />
        <ChatArea />
      </div>
    </ChatProvider>
  );
}
