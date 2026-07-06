import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'InnerVoice — AI Personal Reflection Companion',
  description:
    'InnerVoice is an agentic AI companion that learns your voice, detects your emotions, tracks your goals, and reflects your own inner thoughts back to you.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-slate-950 text-slate-200 antialiased">
        {children}
      </body>
    </html>
  );
}
