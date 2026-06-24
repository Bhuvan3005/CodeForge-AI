import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, ArrowLeft, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { apiLogin, apiRegister, authStore } from '../lib/auth';

type Mode = 'login' | 'register';

export default function LoginPage() {
  const navigate = useNavigate();

  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Redirect if already logged in
  useEffect(() => {
    if (authStore.isLoggedIn()) navigate('/dashboard', { replace: true });
  }, [navigate]);

  const resetFeedback = () => {
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    resetFeedback();

    if (!email.trim() || !password.trim()) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);

    try {
      if (mode === 'login') {
        const data = await apiLogin(email.trim(), password);
        // Persist token + email
        authStore.setSession(data.access_token, email.trim());
        setSuccess('Login successful! Redirecting…');
        setTimeout(() => navigate('/dashboard', { replace: true }), 800);
      } else {
        await apiRegister(email.trim(), password);
        setSuccess('Account created! You can now log in.');
        setMode('login');
        setPassword('');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (m: Mode) => {
    setMode(m);
    resetFeedback();
    setPassword('');
  };

  return (
    <div className="relative h-screen w-screen bg-black overflow-hidden flex flex-col items-center justify-center px-4">

      {/* ── Subtle animated background ──────────────────────── */}
      <div
        className="fixed inset-0 z-0 opacity-30"
        style={{
          backgroundImage: `
            radial-gradient(ellipse 80% 60% at 20% 80%, rgba(99,102,241,0.15) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 20%, rgba(168,85,247,0.12) 0%, transparent 60%)
          `,
        }}
      />
      {/* Grid */}
      <div
        className="fixed inset-0 z-0 opacity-[0.06]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* ── Back to home ─────────────────────────────────────── */}
      <Link
        to="/"
        className="animate-blur-fade-up fixed top-6 left-6 z-20 flex items-center gap-2 liquid-glass rounded-full px-4 py-2 text-sm text-white/70 hover:text-white transition-colors duration-200"
        style={{ animationDelay: '0ms' }}
      >
        <ArrowLeft size={15} />
        Back
      </Link>

      {/* ── Card ─────────────────────────────────────────────── */}
      <div
        className="animate-blur-fade-up relative z-10 w-full max-w-md"
        style={{ animationDelay: '100ms' }}
      >
        {/* Logo + Headline */}
        <div className="text-center mb-8">
          <h1
            className="animate-blur-fade-up text-4xl sm:text-5xl font-normal text-white mb-3"
            style={{ animationDelay: '200ms', letterSpacing: '-0.04em' }}
          >
            CodeForge
          </h1>
          <p
            className="animate-blur-fade-up text-sm text-white/40 tracking-wide"
            style={{ animationDelay: '300ms' }}
          >
            Your AI-powered DSA learning engine
          </p>
        </div>

        {/* Tab switcher */}
        <div
          className="animate-blur-fade-up liquid-glass flex rounded-full p-1 mb-6"
          style={{ animationDelay: '350ms' }}
        >
          {(['login', 'register'] as Mode[]).map((m) => (
            <button
              key={m}
              onClick={() => switchMode(m)}
              className={`flex-1 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                mode === m
                  ? 'bg-white text-black shadow'
                  : 'text-white/50 hover:text-white/80'
              }`}
            >
              {m === 'login' ? 'Sign In' : 'Register'}
            </button>
          ))}
        </div>

        {/* Form card */}
        <div
          className="animate-blur-fade-up liquid-glass rounded-2xl p-6 sm:p-8"
          style={{ animationDelay: '400ms' }}
        >
          <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">

            {/* Email */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="email" className="text-xs text-white/50 uppercase tracking-widest">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); resetFeedback(); }}
                disabled={loading}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-white/30 focus:bg-white/8 transition-all duration-200 disabled:opacity-50"
              />
            </div>

            {/* Password */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="password" className="text-xs text-white/50 uppercase tracking-widest">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); resetFeedback(); }}
                  disabled={loading}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pr-12 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-white/30 focus:bg-white/8 transition-all duration-200 disabled:opacity-50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70 transition-colors"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Feedback */}
            {error && (
              <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
                <AlertCircle size={15} className="shrink-0" />
                {error}
              </div>
            )}
            {success && (
              <div className="flex items-center gap-2 text-emerald-400 text-sm bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3">
                <CheckCircle2 size={15} className="shrink-0" />
                {success}
              </div>
            )}

            {/* Submit */}
            <button
              id="submit-btn"
              type="submit"
              disabled={loading}
              className="flex items-center justify-center gap-2 bg-white text-black rounded-full font-medium py-3 text-sm hover:bg-gray-100 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed mt-1"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  {mode === 'login' ? 'Signing in…' : 'Creating account…'}
                </>
              ) : (
                mode === 'login' ? 'Sign In' : 'Create Account'
              )}
            </button>

          </form>
        </div>

        {/* Footer hint */}
        <p
          className="animate-blur-fade-up text-center text-xs text-white/30 mt-6"
          style={{ animationDelay: '500ms' }}
        >
          {mode === 'login'
            ? "Don't have an account? "
            : 'Already have an account? '}
          <button
            onClick={() => switchMode(mode === 'login' ? 'register' : 'login')}
            className="text-white/60 hover:text-white underline underline-offset-2 transition-colors"
          >
            {mode === 'login' ? 'Register' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}
