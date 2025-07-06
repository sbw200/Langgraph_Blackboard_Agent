"use client"; // MUST BE THE VERY FIRST LINE

import ChatLayout from '@/components/chat/chat-layout';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-background text-foreground">
      <ChatLayout />
    </main>
  );
}