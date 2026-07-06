'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic2 } from 'lucide-react';
import Navbar from '@/components/shared/Navbar';
import VoiceProfileCard from '@/components/voice-profile/VoiceProfileCard';
import LoadingSpinner from '@/components/shared/LoadingSpinner';
import { useAuthStore } from '@/stores/authStore';
import api from '@/lib/api';

export default function VoiceProfilePage() {
  const router = useRouter();
  const { token, loadFromStorage, isLoading } = useAuthStore();
  const [profile, setProfile]         = useState<any>(null);
  const [pageLoading, setPageLoading] = useState(true);

  useEffect(() => { loadFromStorage(); }, [loadFromStorage]);
  useEffect(() => {
    if (!isLoading && !token) router.push('/auth/login');
  }, [isLoading, token, router]);

  useEffect(() => {
    if (!token) return;
    api.get('/api/voice-profile')
      .then(res => setProfile(res.data))
      .catch(err => console.error('Voice profile error:', err))
      .finally(() => setPageLoading(false));
  }, [token]);

  if (isLoading || pageLoading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <LoadingSpinner size="lg" label="Loading voice profile..." /></div>;
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />
      <main className="pl-64 min-h-screen">
        <div className="max-w-3xl mx-auto px-8 py-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-violet-600 flex items-center justify-center">
              <Mic2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Voice Profile</h1>
              <p className="text-sm text-slate-400">How InnerVoice understands and mirrors your writing style</p>
            </div>
          </div>

          {profile ? (
            <VoiceProfileCard profile={profile} />
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center border border-white/5">
              <p className="text-4xl mb-3">🎤</p>
              <p className="text-white font-semibold mb-2">Voice profile not ready yet</p>
              <p className="text-sm text-slate-500">
                Write at least 3 journal entries so InnerVoice can analyze your unique writing style.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
