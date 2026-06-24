import { Link } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';

interface PlaceholderPageProps {
  title: string;
  description: string;
}

export default function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <div className="relative h-screen w-screen bg-black overflow-hidden flex flex-col items-center justify-center">

      {/* ── Animated background grid ─────────────────────────── */}
      <div
        className="fixed inset-0 z-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* ── Radial glow ──────────────────────────────────────── */}
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 60% 50% at 50% 50%, rgba(120,80,255,0.12) 0%, transparent 70%)',
        }}
      />

      {/* ── Content ──────────────────────────────────────────── */}
      <div className="relative z-10 flex flex-col items-center text-center px-6 max-w-2xl">

        {/* Badge */}
        <div
          className="animate-blur-fade-up liquid-glass flex items-center gap-2 rounded-full px-4 py-2 mb-8 text-xs text-white/60 uppercase tracking-widest"
          style={{ animationDelay: '0ms' }}
        >
          <Sparkles size={14} />
          CodeForge
        </div>

        {/* Title */}
        <h1
          className="animate-blur-fade-up text-5xl sm:text-6xl md:text-7xl font-normal text-white mb-6"
          style={{
            animationDelay: '150ms',
            letterSpacing: '-0.04em',
            lineHeight: 1.05,
          }}
        >
          {title}
        </h1>

        {/* Description */}
        <p
          className="animate-blur-fade-up text-lg sm:text-xl text-gray-400 mb-12 leading-relaxed"
          style={{ animationDelay: '300ms' }}
        >
          {description}
        </p>

        {/* Coming Soon card */}
        <div
          className="animate-blur-fade-up liquid-glass rounded-2xl px-8 py-6 mb-10 w-full"
          style={{ animationDelay: '450ms' }}
        >
          <p className="text-sm text-white/40 uppercase tracking-widest mb-2">Status</p>
          <p className="text-white font-medium text-lg">Coming Soon</p>
          <p className="text-white/50 text-sm mt-1">
            This section is under active development. Check back shortly.
          </p>
        </div>

        {/* Back button */}
        <Link
          to="/"
          id="back-home-btn"
          className="animate-blur-fade-up flex items-center gap-2 liquid-glass rounded-full px-6 py-3 text-sm text-white/80 hover:text-white transition-colors duration-200"
          style={{ animationDelay: '600ms' }}
        >
          <ArrowLeft size={16} />
          Back to Home
        </Link>
      </div>
    </div>
  );
}
