'use client';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import {
  BookOpen, LayoutDashboard, Target, Brain,
  MessageSquare, Database, Mic2, LogOut, Sparkles
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

const navItems = [
  { href: '/journal',       icon: BookOpen,        label: 'Journal' },
  { href: '/dashboard',     icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/goals',         icon: Target,          label: 'Goals' },
  { href: '/memories',      icon: Database,        label: 'Memories' },
  { href: '/mirror-me',     icon: Brain,           label: 'Mirror Me' },
  { href: '/voice-profile', icon: Mic2,            label: 'Voice Profile' },
  { href: '/chat',          icon: MessageSquare,   label: 'Chat' },
];

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout, loadFromStorage } = useAuthStore();

  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-64 glass-panel border-r border-white/10 flex flex-col z-50">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">InnerVoice</h1>
            <p className="text-xs text-slate-400">AI Companion</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, icon: Icon, label }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-200 group ${
                active
                  ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className={`w-4 h-4 ${active ? 'text-violet-400' : 'group-hover:text-violet-400'} transition-colors`} />
              <span className="text-sm font-medium">{label}</span>
              {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-violet-400" />}
            </Link>
          );
        })}
      </nav>

      {/* User */}
      {user && (
        <div className="px-3 py-4 border-t border-white/10">
          <div className="px-4 py-3 rounded-xl bg-white/5 mb-2">
            <p className="text-sm font-semibold text-white truncate">{user.username}</p>
            <p className="text-xs text-slate-400 truncate">{user.email}</p>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-xs text-violet-300">🔥 {user.streak_count} day streak</span>
              <span className="text-xs text-slate-500">·</span>
              <span className="text-xs text-slate-400">{user.total_messages} messages</span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all text-sm"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      )}
    </aside>
  );
}
