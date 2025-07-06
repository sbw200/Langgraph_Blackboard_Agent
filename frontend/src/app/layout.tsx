// frontend/src/app/layout.tsx
// This is your RootLayout file.
import type { Metadata } from 'next';
import './globals.css'; // Ensure this path is correct
import { Toaster } from "@/components/ui/toaster"; // Ensure this path is correct

export const metadata: Metadata = {
  title: 'BBChatt',
  description: 'A simple, responsive web chatbot.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Ensure these font links are correct and accessible */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet" />
      </head>
      <body className="font-body antialiased">
        {children}
        <Toaster /> {/* This component is rendered here */}
      </body>
    </html>
  );
}