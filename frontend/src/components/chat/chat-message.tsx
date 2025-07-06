import { Message } from '@/types';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Bot, User } from 'lucide-react';
// New
interface ChatMessageProps {
  message: Message;
  isLoading?: boolean;
}

export default function ChatMessage({ message, isLoading = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  return (
    <div
      className={cn('flex items-start gap-3', {
        'justify-end': isUser,
      })}
    >
      {!isUser && (
        <Avatar className="w-8 h-8 border border-primary/20">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <Bot className="w-5 h-5" />
          </AvatarFallback>
        </Avatar>
      )}
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-md',
          {
            'bg-accent text-accent-foreground rounded-br-none': isUser,
            'bg-card text-card-foreground rounded-bl-none border': !isUser,
          }
        )}
      >
        {isLoading ? (
          <div className="flex items-center justify-center gap-1.5">
            <span className="h-2 w-2 animate-pulse rounded-full bg-muted-foreground/50 [animation-delay:-0.3s]"></span>
            <span className="h-2 w-2 animate-pulse rounded-full bg-muted-foreground/50 [animation-delay:-0.15s]"></span>
            <span className="h-2 w-2 animate-pulse rounded-full bg-muted-foreground/50"></span>
          </div>
        ) : (
          message.content
        )}
      </div>
      {isUser && (
        <Avatar className="w-8 h-8 border border-accent/20">
          <AvatarFallback className="bg-accent text-accent-foreground">
            <User className="w-5 h-5" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
