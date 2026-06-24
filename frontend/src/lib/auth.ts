/**
 * Lightweight auth store using localStorage for token persistence.
 * No external state lib needed — just a simple reactive wrapper.
 */

const TOKEN_KEY = 'cf_access_token';
const EMAIL_KEY = 'cf_user_email';

export const authStore = {
  getToken: (): string | null => localStorage.getItem(TOKEN_KEY),
  getEmail: (): string | null => localStorage.getItem(EMAIL_KEY),

  isLoggedIn: (): boolean => !!localStorage.getItem(TOKEN_KEY),

  setSession: (token: string, email: string) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(EMAIL_KEY, email);
  },

  clearSession: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EMAIL_KEY);
  },
};

/** Base URL for all API calls */
export const API_BASE = 'http://localhost:8000';

/** Typed API response for /auth/login */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/**
 * Login via OAuth2PasswordRequestForm (x-www-form-urlencoded)
 * Maps email → username field as required by FastAPI OAuth2PasswordBearer.
 */
export async function apiLogin(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.append('username', email);   // FastAPI OAuth2 uses 'username'
  body.append('password', password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(err.detail ?? 'Login failed');
  }

  return res.json();
}

/**
 * Register via JSON body
 */
export async function apiRegister(email: string, password: string): Promise<string> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail ?? 'Registration failed');
  }

  return res.json(); // returns the new user's id string
}
