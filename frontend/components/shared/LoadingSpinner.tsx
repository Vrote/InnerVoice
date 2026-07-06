export default function LoadingSpinner({ size = 'md', label }: { size?: 'sm' | 'md' | 'lg'; label?: string }) {
  const sizes = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' };
  return (
    <div className="flex flex-col items-center gap-3">
      <div className={`${sizes[size]} rounded-full border-2 border-violet-500/30 border-t-violet-500 animate-spin`} />
      {label && <p className="text-sm text-slate-400 animate-pulse">{label}</p>}
    </div>
  );
}
