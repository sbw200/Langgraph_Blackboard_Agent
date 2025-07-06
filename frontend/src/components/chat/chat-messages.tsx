"use client";
// New
import { useRef, useEffect } from 'react';
import { Message } from '@/types';
import { ScrollArea } from '@/components/ui/scroll-area';
import ChatMessage from './chat-message';
import { AnimatePresence, motion } from 'framer-motion';

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

export default function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const scrollViewportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollViewportRef.current) {
      scrollViewportRef.current.scrollTo({
        top: scrollViewportRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, isLoading]);

  return (
    <ScrollArea className="h-full" viewportRef={scrollViewportRef}>
      <div className="p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              layout
              initial={{ opacity: 0, scale: 0.8, y: 50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: -50 }}
              transition={{
                opacity: { duration: 0.2 },
                layout: {
                  type: "spring",
                  bounce: 0.3,
                  duration: index * 0.05 + 0.4,
                },
              }}
            >
              <ChatMessage message={message} />
            </motion.div>
          ))}
          {isLoading && (
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                opacity: { duration: 0.3 },
                layout: {
                  type: "spring",
                  bounce: 0.3,
                  duration: 0.5,
                },
              }}
            >
              <ChatMessage message={{ id: 'loading', role: 'assistant', content: '...' }} isLoading={true} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </ScrollArea>
  );
}
