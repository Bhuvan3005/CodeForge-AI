import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HeroSection from './pages/HeroSection';
import LoginPage from './pages/LoginPage';
import PlaceholderPage from './pages/PlaceholderPage';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<HeroSection />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/problems" element={<PlaceholderPage title="Problems" description="Ace your interviews with our AI-curated DSA problem sets." />} />
        <Route path="/roadmap" element={<PlaceholderPage title="Roadmap" description="Follow curated paths to master DSA concepts." />} />
        <Route path="/topics" element={<PlaceholderPage title="Topics" description="Essential topics that AI uses to assess your skills." />} />
        <Route path="/about-us" element={<PlaceholderPage title="About Us" description="Get to know the team behind CodeForge and our mission to democratize DSA education." />} />

        {/* Protected routes — require login */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <PlaceholderPage title="Dashboard" description="Track your progress and manage your learning journey." />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <PlaceholderPage title="My Profile" description="Manage your account, preferences, and learning history." />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
