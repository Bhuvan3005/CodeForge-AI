import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Menu,
  X,
} from 'lucide-react';

const VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260406_094145_4a271a6c-3869-4f1c-8aa7-aeb0cb227994.mp4';

const NAV_LINKS = [
  { label: 'Problems', href: '/problems' },
  { label: 'Roadmap', href: '/roadmap' },
  { label: 'Topics', href: '/topics' },
  { label: 'About Us', href: '/about-us' },
  { label: 'Dashboard', href: '/dashboard' },
];

export default function HeroSection() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="relative h-screen w-screen bg-black overflow-hidden flex flex-col">

      {/* ── Background Video ──────────────────────────────────── */}
      <video
        className="fixed inset-0 w-full h-full object-cover z-0"
        src={VIDEO_URL}
        autoPlay
        muted
        loop
        playsInline
      />

      {/* ── Bottom Blur Overlay (mask: bottom fade only) ──────── */}
      <div className="bottom-blur-overlay" />

      {/* ── Navbar ───────────────────────────────────────────── */}
      <nav
        className="relative z-50 flex items-center justify-between px-4 sm:px-6 md:px-12 py-4 md:py-6"
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Logo */}
        <Link
          to="/"
          className="animate-blur-fade-up text-white font-semibold text-lg tracking-[0.15em] uppercase select-none"
          style={{ animationDelay: '0ms' }}
          aria-label="CodeForge Home"
        >
          CodeForge
        </Link>

        {/* Desktop Nav Links (lg and up) */}
        <ul className="hidden lg:flex items-center gap-8" role="list">
          {NAV_LINKS.map((link, i) => (
            <li key={link.href}>
              <Link
                to={link.href}
                className="animate-blur-fade-up text-sm text-white/80 hover:text-white transition-colors duration-200"
                style={{ animationDelay: `${100 + i * 50}ms` }}
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Right Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Search Button — hidden below sm */}
          {/* <Link
            to="/search"
            className="animate-blur-fade-up hidden sm:flex items-center gap-2 liquid-glass rounded-full px-4 md:px-6 py-2 text-sm text-white/90 hover:text-white transition-colors duration-200 cursor-pointer"
            style={{ animationDelay: '350ms' }}
            aria-label="Search"
            id="search-btn"
          >
            <Search size={18} />
            <span className="hidden md:inline">Search</span>
          </Link> */}

          {/* Profile Button — hidden below sm */}
          <Link
            to="/profile"
            className="animate-blur-fade-up hidden sm:flex items-center justify-center liquid-glass rounded-full w-10 h-10 text-white/90 hover:text-white transition-colors duration-200 cursor-pointer"
            style={{ animationDelay: '400ms' }}
            aria-label="User profile"
            id="profile-btn"
          >
            <User size={18} />
          </Link>

          {/* Hamburger — shown below lg */}
          <button
            id="hamburger-btn"
            className="animate-blur-fade-up lg:hidden flex items-center justify-center liquid-glass rounded-full w-10 h-10 text-white/90 hover:text-white transition-colors duration-200 cursor-pointer"
            style={{ animationDelay: '350ms' }}
            onClick={() => setMenuOpen((o) => !o)}
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
          >
            <span
              className={`absolute transition-all duration-500 ease-out ${
                menuOpen
                  ? 'opacity-100 rotate-0 scale-100'
                  : 'opacity-0 rotate-180 scale-50'
              }`}
            >
              <X size={18} />
            </span>
            <span
              className={`absolute transition-all duration-500 ease-out ${
                menuOpen
                  ? 'opacity-0 -rotate-180 scale-50'
                  : 'opacity-100 rotate-0 scale-100'
              }`}
            >
              <Menu size={18} />
            </span>
          </button>
        </div>
      </nav>

      {/* ── Mobile Menu Dropdown ──────────────────────────────── */}
      <div
        id="mobile-menu"
        className={`lg:hidden absolute left-0 right-0 top-[72px] z-40 transition-all duration-500 ease-out ${
          menuOpen
            ? 'translate-y-0 opacity-100 pointer-events-auto'
            : '-translate-y-4 opacity-0 pointer-events-none'
        }`}
        role="menu"
        aria-hidden={!menuOpen}
      >
        <div className="bg-gray-900/95 backdrop-blur-lg border-t border-b border-gray-800 shadow-2xl px-4 sm:px-6 py-4">
          {/* Nav links */}
          <ul className="flex flex-col gap-1" role="list">
            {NAV_LINKS.map((link, i) => (
              <li key={link.href}>
                <Link
                  to={link.href}
                  className={`flex items-center py-3 px-3 rounded-lg text-sm text-white/80 hover:text-white hover:bg-gray-800/50 transition-all duration-200 ${
                    menuOpen ? 'animate-slide-in' : ''
                  }`}
                  style={{ animationDelay: `${i * 50}ms` }}
                  onClick={() => setMenuOpen(false)}
                  role="menuitem"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>

          {/* Search & Profile — visible below sm */}
          <div className="sm:hidden mt-4 pt-4 border-t border-gray-800 flex items-center gap-3">
            {/* <Link
              to="/search"
              className="flex-1 flex items-center justify-center gap-2 liquid-glass rounded-full py-2.5 text-sm text-white/90 hover:text-white transition-colors duration-200"
              onClick={() => setMenuOpen(false)}
              aria-label="Search"
            >
              <Search size={16} />
              Search
            </Link> */}
            <Link
              to="/profile"
              className="flex items-center justify-center liquid-glass rounded-full w-10 h-10 text-white/90 hover:text-white transition-colors duration-200"
              onClick={() => setMenuOpen(false)}
              aria-label="User profile"
            >
              <User size={16} />
            </Link>
          </div>
        </div>
      </div>

      {/* ── Hero Content (bottom of viewport) ────────────────── */}
      <div className="relative z-10 flex-1 flex flex-col justify-end px-4 sm:px-6 md:px-12 pb-8 md:pb-16">
        <div className="flex flex-col md:flex-row items-end gap-8">

          {/* Left: Metadata + Title + Description + CTAs */}
          <div className="flex-1">

            {/* Metadata row */}
            <div
              className="animate-blur-fade-up flex flex-wrap items-center gap-3 sm:gap-6 mb-6 md:mb-8 text-xs sm:text-sm text-white/90"
              style={{ animationDelay: '300ms' }}
            >
              <span className="flex items-center gap-1.5 font-medium">
                
                ○ AI-Powered Learning
              </span>
              <span className="flex items-center gap-1.5">
                
                ○ Smart Courses
              </span>
              <span className="flex items-center gap-1.5">
                
                ○ Designed for you
              </span>
            </div>

            {/* Title */}
            <h1
              className="animate-blur-fade-up text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-normal text-white mb-4 md:mb-6"
              style={{
                animationDelay: '400ms',
                letterSpacing: '-0.04em',
                lineHeight: 1.05,
              }}
            >
              Think Better.
              <br />
              Solve Smarter.
            </h1>

            {/* Description */}
            <p
              className="animate-blur-fade-up text-base sm:text-lg md:text-xl text-gray-400 mb-6 md:mb-12 max-w-2xl"
              style={{ animationDelay: '500ms' }}
            >
              Your roadmap to DSA excellence. Guided By AI.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-3 sm:gap-4">
              <Link
                to="/login"
                id="watch-now-btn"
                className="animate-blur-fade-up flex items-center gap-2 bg-white text-black rounded-full font-medium px-6 sm:px-8 py-2.5 sm:py-3 text-sm hover:bg-gray-200 transition-colors duration-200"
                style={{ animationDelay: '600ms' }}
              >
                <User size={18} fill="black" />
                Let's Crack It.
              </Link>
              <Link
                to="/about-us"
                id="learn-more-btn"
                className="animate-blur-fade-up liquid-glass flex items-center gap-2 rounded-full font-medium px-6 sm:px-8 py-2.5 sm:py-3 text-sm text-white/90 hover:text-white transition-colors duration-200"
                style={{ animationDelay: '700ms' }}
              >
                Learn More
              </Link>
            </div>
          </div>

          {/* Right: Stacked Code Editor Images */}
          <div
            className="animate-blur-fade-up hidden md:flex items-end justify-end relative"
            style={{ animationDelay: '600ms', width: '540px', height: '360px', flexShrink: 0 }}
          >
            {/* Back image — rotated counter-clockwise */}
            <img
              src="/assets/ChatGPT Image Jun 24, 2026, 07_59_25 PM.png"
              alt="Code editor screenshot"
              style={{
                position: 'absolute',
                bottom: '20px',
                right: '30px',
                width: '420px',
                borderRadius: '16px',
                transform: 'rotate(-7deg) translateY(8px)',
                boxShadow: '0 25px 60px rgba(0,0,0,0.75)',
                opacity: 0.82,
                border: '1px solid rgba(255,255,255,0.08)',
              }}
            />
            {/* Front image — rotated clockwise */}
            <img
              src="/assets/ChatGPT Image Jun 24, 2026, 08_01_02 PM.png"
              alt="LeetCode problem screenshot"
              style={{
                position: 'absolute',
                bottom: '40px',
                right: '0px',
                width: '400px',
                borderRadius: '16px',
                transform: 'rotate(5deg)',
                boxShadow: '0 32px 72px rgba(0,0,0,0.85)',
                border: '1px solid rgba(255,255,255,0.13)',
              }}
            />
          </div>

        </div>
      </div>
    </div>
  );
}
