//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/pages/Login.tsx
//*       Login form for user authentication
//*       Config-driven authentication using AuthContext
//*........................................................

import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, X, Home } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui_custom/button';
import { Label } from '@/components/ui/label';
import { BaseModal } from '@/components/modals/BaseModal';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSignUpModal, setShowSignUpModal] = useState(false);
  const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);
  
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Redirect after login
  const from = (location.state as any)?.from?.pathname || '/';
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const success = await login(username, password);
      
      if (success) {
        navigate(from, { replace: true });
      } else {
        setError('Invalid login credentials');
      }
    } catch (err) {
      setError('Login error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="w-full max-w-md bg-card rounded-xl shadow-lg border border-border p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <img 
                src="/assets/logo.png" 
                alt="Sopira Magic Logo" 
                className="h-24 object-contain"
              />
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Sign In
            </h1>
            <p className="text-sm text-muted-foreground">
              Enter your login credentials
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            {/* Username Field */}
            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-medium">
                Username
              </Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading}
                className="w-full"
                placeholder="Enter username"
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="w-full pr-10"
                  placeholder="Enter password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  disabled={isLoading}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff size={18} className="pointer-events-none" />
                  ) : (
                    <Eye size={18} className="pointer-events-none" />
                  )}
                </button>
              </div>
            </div>

            {/* Sign In Button */}
            <Button
              type="submit"
              disabled={isLoading}
              variant="solid"
              className="w-full"
            >
              {isLoading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            {/* Sign Up Button */}
            <Button
              type="button"
              onClick={() => setShowSignUpModal(true)}
              disabled={isLoading}
              variant="default"
              className="w-full"
            >
              Sign Up
            </Button>

            {/* Forgot Password Link */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => setShowForgotPasswordModal(true)}
                className="text-sm text-primary hover:underline"
                disabled={isLoading}
              >
                Forgot password?
              </button>
            </div>

            {/* Home Button */}
            <Link to="/" className="block">
              <Button
                type="button"
                variant="ghost"
                className="w-full"
                disabled={isLoading}
              >
                <Home size={18} className="mr-2" />
                Home
              </Button>
            </Link>
          </form>
        </div>
      </div>

      {/* Sign Up Modal */}
      <SignUpModal
        open={showSignUpModal}
        onClose={() => setShowSignUpModal(false)}
      />

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        open={showForgotPasswordModal}
        onClose={() => setShowForgotPasswordModal(false)}
      />
    </>
  );
};

// Sign Up Modal Component
interface SignUpModalProps {
  open: boolean;
  onClose: () => void;
}

const SignUpModal: React.FC<SignUpModalProps> = ({ open, onClose }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.username || !formData.password) {
      setError('Username and password are required');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.email && !formData.email.includes('@')) {
      setError('Please enter a valid email address. The @ symbol is missing.');
      return;
    }

    setIsLoading(true);

    try {
      const result = await signup(
        formData.username,
        formData.password,
        formData.email || undefined,
        formData.first_name || undefined,
        formData.last_name || undefined
      );

      if (result.success) {
        onClose();
        // Redirect to companies page for new user to create first company
        navigate('/companies', { 
          replace: true,
          state: { isNewUser: true } // Flag for empty state message
        });
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (err) {
      setError('Registration error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <BaseModal open={open} onClose={onClose} size="md">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-foreground">Sign Up</h2>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
            <X size={18} />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_name" className="text-sm font-medium">
                First Name
              </Label>
              <Input
                id="first_name"
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                disabled={isLoading}
                placeholder="First name (optional)"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name" className="text-sm font-medium">
                Last Name
              </Label>
              <Input
                id="last_name"
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                disabled={isLoading}
                placeholder="Last name (optional)"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="username" className="text-sm font-medium">
              Username <span className="text-destructive">*</span>
            </Label>
            <Input
              id="username"
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              disabled={isLoading}
              required
              placeholder="Enter username"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              disabled={isLoading}
              placeholder="Enter email (optional)"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium">
              Password <span className="text-destructive">*</span>
            </Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                disabled={isLoading}
                required
                placeholder="Enter password (min. 8 characters)"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                disabled={isLoading}
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff size={18} className="pointer-events-none" />
                ) : (
                  <Eye size={18} className="pointer-events-none" />
                )}
              </button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-sm font-medium">
              Confirm Password <span className="text-destructive">*</span>
            </Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                disabled={isLoading}
                required
                placeholder="Confirm password"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                disabled={isLoading}
                tabIndex={-1}
              >
                {showConfirmPassword ? (
                  <EyeOff size={18} className="pointer-events-none" />
                ) : (
                  <Eye size={18} className="pointer-events-none" />
                )}
              </button>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="default"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="solid"
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Signing up...
                </>
              ) : (
                'Sign Up'
              )}
            </Button>
          </div>
        </form>
      </div>
    </BaseModal>
  );
};

// Forgot Password Modal Component
interface ForgotPasswordModalProps {
  open: boolean;
  onClose: () => void;
}

const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({ open, onClose }) => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { forgotPassword } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!email) {
      setError('Please enter your email address');
      return;
    }

    setIsLoading(true);

    try {
      const result = await forgotPassword(email);

      if (result.success) {
        setSuccess(true);
      } else {
        setError(result.error || 'Failed to send reset email');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <BaseModal open={open} onClose={onClose} size="md">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-foreground">Forgot Password</h2>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
            <X size={18} />
          </Button>
        </div>

        {success ? (
          <div className="space-y-4">
            <div className="p-4 rounded-md bg-primary/10 border border-primary/20 text-foreground text-sm">
              If an account with this email exists, a password reset link has been sent to your email address.
            </div>
            <Button onClick={onClose} variant="solid" className="w-full">
              Close
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Enter your email address and we'll send you a link to reset your password.
            </p>

            {error && (
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="reset-email" className="text-sm font-medium">
                Email Address
              </Label>
              <Input
                id="reset-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
                placeholder="Enter your email"
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="default"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="solid"
                disabled={isLoading}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Sending...
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </Button>
            </div>
          </form>
        )}
      </div>
    </BaseModal>
  );
};

export default Login;
