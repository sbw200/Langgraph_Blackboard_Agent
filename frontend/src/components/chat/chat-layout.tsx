"use client";

// // New
import { useState } from 'react';
import { Message } from '@/types';
import { v4 as uuidv4 } from 'uuid';
import ChatMessages from '@/components/chat/chat-messages';
import ChatInput from '@/components/chat/chat-input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import Aurora from "@/components/ui/Aurora"; // adjust path if needed


// IMPORTANT: Configure your FastAPI Backend URL here
// During local development, this might be something like 'http://localhost:8000'
// Once deployed, it will be your FastAPI service's public URL, e.g., 'https://your-fastapi-app.cloud.run'
const FASTAPI_BACKEND_URL = process.env.NEXT_PUBLIC_FASTAPI_BACKEND_URL || 'http://localhost:8000'; // Default for local testing

interface ChatRequest {
  message: string;
}

interface ChatResponse {
  response: string;
  error?: boolean;
}

export default function ChatLayout() {
  const [messages, setMessages] = useState<Message[]>([
      { id: uuidv4(), role: 'assistant', content: "Hello! Type a message to start our conversation." }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      // MODIFIED: Changed fetch URL to point to your FastAPI backend
      const response = await fetch(`${FASTAPI_BACKEND_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: content } as ChatRequest),
      });

      if (!response.ok) {
        // If the server response indicates an error (e.g., 4xx, 5xx)
        let errorDetail = `Server responded with status: ${response.status}`;
        try {
            const errorData = await response.json();
            if (errorData.detail) {
                errorDetail += ` - Detail: ${errorData.detail}`;
            } else if (errorData.message) {
                errorDetail += ` - Message: ${errorData.message}`;
            }
        } catch (jsonError) {
            // If response is not JSON, just use status
            console.warn("Server error response was not JSON:", jsonError);
        }
        throw new Error(errorDetail);
      }

      const data: ChatResponse = await response.json();

      // Check for an 'error' flag in the response body from the backend
      if (data.error) {
        toast({
          variant: "destructive",
          title: "Bot Error",
          description: data.response || "The chatbot encountered an error.",
        });
        const errorMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: data.response || "I'm sorry, I couldn't process that. Please try again.",
        };
        setMessages((prev) => [...prev, errorMessage]);
      } else {
        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: data.response,
        };
        setMessages((prevMessages) => [...prevMessages, assistantMessage]);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
        toast({
          variant: "destructive",
          title: "Network Error",
          description: error instanceof Error ? error.message : "Could not connect to the server. Please try again later.",
        });
        const errorMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: "I'm having trouble connecting to the chatbot. Please check your network and try again.",
        };
        setMessages((prev) => [...prev, errorMessage]);

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="relative w-full max-w-2xl h-full md:h-[90vh] flex flex-col shadow-2xl rounded-xl bg-card overflow-hidden">
  {/* Aurora background animation */}
  <Aurora
    colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
    blend={0.5}
    amplitude={1.0}
    speed={0.5}
  />

  {/* Chat content */}
  <CardHeader className="border-b relative z-10">
    <CardTitle className="text-2xl font-headline text-primary">BBChat</CardTitle>
  </CardHeader>
  <CardContent className="flex-grow overflow-hidden p-0 relative z-10">
    <ChatMessages messages={messages} isLoading={isLoading} />
  </CardContent>
  <CardFooter className="p-4 border-t relative z-10">
    <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
  </CardFooter>
</Card>

  );
}


// import { useState, useRef } from 'react'; // Import useRef
// import { Message } from '@/types';
// import { v4 as uuidv4 } from 'uuid';
// import ChatMessages from '@/components/chat/chat-messages';
// import ChatInput from '@/components/chat/chat-input';
// import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
// import { useToast } from '@/hooks/use-toast';
// import Aurora from "@/components/ui/Aurora"; // adjust path if needed


// // IMPORTANT: Configure your FastAPI Backend URL here
// // During local development, this might be something like 'http://localhost:8000'
// // Once deployed, it will be your FastAPI service's public URL, e.g., 'https://your-fastapi-app.cloud.run'
// const FASTAPI_BACKEND_URL = process.env.NEXT_PUBLIC_FASTAPI_BACKEND_URL || 'http://localhost:8000'; // Default for local testing

// interface ChatRequest {
//   message: string;
//   thread_id?: string; // Add thread_id to the request interface
// }

// interface ChatResponse {
//   response: string;
//   error?: boolean;
//   thread_id?: string; // Backend will return this
// }

// export default function ChatLayout() {
//   const [messages, setMessages] = useState<Message[]>([
//       { id: uuidv4(), role: 'assistant', content: "Hello! Type a message to start our conversation." }
//   ]);
//   const [isLoading, setIsLoading] = useState(false);
//   const { toast } = useToast();

//   // Use a ref to store the thread_id so it persists across renders
//   // and can be accessed without causing re-renders when updated.
//   const threadIdRef = useRef<string>(uuidv4()); // Initialize with a new UUID

//   const handleSendMessage = async (content: string) => {
//     if (!content.trim()) return;

//     const userMessage: Message = {
//       id: uuidv4(),
//       role: 'user',
//       content,
//     };

//     setMessages((prevMessages) => [...prevMessages, userMessage]);
//     setIsLoading(true);

//     // Add a temporary loading message for the assistant
//     const loadingMessageId = uuidv4();
//     setMessages((prevMessages) => [
//       ...prevMessages,
//       { id: loadingMessageId, role: 'assistant', content: '...' },
//     ]);

//     try {
//       const response = await fetch(`${FASTAPI_BACKEND_URL}/chat`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         // MODIFIED: Send the thread_id with the request
//         body: JSON.stringify({ message: content, thread_id: threadIdRef.current } as ChatRequest),
//       });

//       if (!response.ok) {
//         let errorDetail = `Server responded with status: ${response.status}`;
//         try {
//             const errorData = await response.json();
//             if (errorData.detail) {
//                 errorDetail += ` - Detail: ${errorData.detail}`;
//             } else if (errorData.response) { // Use 'response' field from backend error
//                 errorDetail += ` - Message: ${errorData.response}`;
//             }
//         } catch (jsonError) {
//             console.warn("Server error response was not JSON:", jsonError);
//         }
//         throw new Error(errorDetail);
//       }

//       const data: ChatResponse = await response.json();

//       // Check for an 'error' flag in the response body from the backend
//       if (data.error) {
//         toast({
//           variant: "destructive",
//           title: "Bot Error",
//           description: data.response || "The chatbot encountered an error.",
//         });
//         // Update the loading message with the error message
//         setMessages((prev) =>
//           prev.map((msg) =>
//             msg.id === loadingMessageId
//               ? { ...msg, content: data.response || "I'm sorry, I couldn't process that. Please try again." }
//               : msg
//           )
//         );
//       } else {
//         // Update the loading message with the actual assistant response
//         setMessages((prevMessages) =>
//           prevMessages.map((msg) =>
//             msg.id === loadingMessageId
//               ? { ...msg, content: data.response }
//               : msg
//           )
//         );
//         // If the backend returns a new thread_id (e.g., for the first message), update the ref
//         if (data.thread_id && data.thread_id !== threadIdRef.current) {
//             threadIdRef.current = data.thread_id;
//         }
//       }

//     } catch (error) {
//       console.error('Failed to send message:', error);
//         toast({
//           variant: "destructive",
//           title: "Network Error",
//           description: error instanceof Error ? error.message : "Could not connect to the server. Please try again later.",
//         });
//         // Replace the loading message with a network error message
//         setMessages((prev) =>
//           prev.map((msg) =>
//             msg.id === loadingMessageId
//               ? { ...msg, content: "I'm having trouble connecting to the chatbot. Please check your network and try again." }
//               : msg
//           )
//         );

//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <Card className="relative w-full max-w-2xl h-full md:h-[90vh] flex flex-col shadow-2xl rounded-xl bg-card overflow-hidden">
//       {/* Aurora background animation */}
//       <Aurora
//         colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
//         blend={0.5}
//         amplitude={1.0}
//         speed={0.5}
//       />

//       {/* Chat content */}
//       <CardHeader className="border-b relative z-10">
//         <CardTitle className="text-2xl font-headline text-primary">BBChat</CardTitle>
//       </CardHeader>
//       <CardContent className="flex-grow overflow-hidden p-0 relative z-10">
//         <ChatMessages messages={messages} isLoading={isLoading} />
//       </CardContent>
//       <CardFooter className="p-4 border-t relative z-10">
//         <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
//       </CardFooter>
//     </Card>

//   );
// }

{/* <Card className="w-full max-w-2xl h-full md:h-[90vh] flex flex-col shadow-2xl rounded-xl bg-card">
      <CardHeader className="border-b">
        <CardTitle className="text-2xl font-headline text-primary">ChattyNext</CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-hidden p-0">
        <ChatMessages messages={messages} isLoading={isLoading} />
      </CardContent>
      <CardFooter className="p-4 border-t">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </CardFooter>
    </Card> */}