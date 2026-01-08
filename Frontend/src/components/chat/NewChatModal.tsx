import { useState } from 'react';
import { useChat } from '@/contexts/ChatContext';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

const PERSONALITIES = [
  { value: 'friend', label: 'Friend' },
  { value: 'girlfriend', label: 'Girlfriend' },
  { value: 'guide', label: 'Mentor' },
  { value: 'bully', label: 'Bully' },
];

interface NewChatModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function NewChatModal({ open, onOpenChange }: NewChatModalProps) {
  const [chatName, setChatName] = useState('');
  const [personality, setPersonality] = useState('general');
  const [isLoading, setIsLoading] = useState(false);
  const { createChat, selectChat } = useChat();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!chatName.trim()) {
      toast({
        title: 'Chat name required',
        description: 'Please enter a name for your chat.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    try {
      const newChat = await createChat(chatName.trim(), personality);
      await selectChat(newChat.chat_id);
      onOpenChange(false);
      setChatName('');
      setPersonality('general');
      toast({
        title: 'Chat created',
        description: `"${chatName}" is ready to use.`,
      });
    } catch (error: any) {
      toast({
        title: 'Failed to create chat',
        description: error.response?.data?.detail || 'Something went wrong.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>New Chat</DialogTitle>
          <DialogDescription>
            Create a new conversation with a specific AI personality.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="chatName">Chat Name</Label>
              <Input
                id="chatName"
                placeholder="e.g., Python Help, Math Homework"
                value={chatName}
                onChange={(e) => setChatName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="personality">Personality</Label>
              <Select value={personality} onValueChange={setPersonality}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a personality" />
                </SelectTrigger>
                <SelectContent>
                  {PERSONALITIES.map((p) => (
                    <SelectItem key={p.value} value={p.value}>
                      {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" className="bg-accent hover:bg-accent/90" disabled={isLoading}>
              {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
              Create
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
