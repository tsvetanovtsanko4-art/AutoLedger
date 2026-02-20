import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// RFC-5321 inspired email regex — covers the vast majority of valid addresses
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const RegisterForm = () => {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState(null);
    const [fieldErrors, setFieldErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        // --- Field-level validation ---
        const errors = {};

        if (!email.trim()) {
            errors.email = 'Email is required.';
        } else if (/\s/.test(email)) {
            errors.email = 'Email must not contain spaces.';
        } else if (!EMAIL_REGEX.test(email.trim())) {
            errors.email = 'Please enter a valid email address (e.g. you@example.com).';
        }

        if (!password) {
            errors.password = 'Password is required.';
        } else if (/\s/.test(password)) {
            errors.password = 'Password must not contain spaces.';
        }

        if (!confirm) {
            errors.confirm = 'Please confirm your password.';
        } else if (/\s/.test(confirm)) {
            errors.confirm = 'Confirm password must not contain spaces.';
        } else if (password && password !== confirm) {
            errors.confirm = 'Passwords do not match.';
        }

        if (Object.keys(errors).length > 0) {
            setFieldErrors(errors);
            return;
        }

        setFieldErrors({});
        setLoading(true);
        try {
            await register(email.trim(), password);
            navigate('/home');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 to-slate-900 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
                <div className="text-center mb-8">
                    <div className="text-5xl mb-3">🚗</div>
                    <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
                    <p className="text-gray-500 mt-2">Start tracking your car expenses today</p>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm" data-testid="register-error">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                            type="text"
                            value={email}
                            onChange={e => { const v = e.target.value.replace(/\s/g, ''); setEmail(v); setFieldErrors(prev => ({ ...prev, email: undefined })); }}
                            className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition ${fieldErrors.email ? 'border-red-400 bg-red-50' : 'border-gray-300'}`}
                            data-testid="input-email"
                            placeholder="you@example.com"
                        />
                        {fieldErrors.email && <p className="text-red-600 text-xs mt-1" data-testid="error-email">{fieldErrors.email}</p>}
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onKeyDown={e => { if (e.key === ' ') e.preventDefault(); }}
                            onChange={e => { setPassword(e.target.value); setFieldErrors(prev => ({ ...prev, password: undefined })); }}
                            className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition ${fieldErrors.password ? 'border-red-400 bg-red-50' : 'border-gray-300'}`}
                            data-testid="input-password"
                            placeholder="••••••••"
                        />
                        {fieldErrors.password && <p className="text-red-600 text-xs mt-1" data-testid="error-password">{fieldErrors.password}</p>}
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                        <input
                            type="password"
                            value={confirm}
                            onKeyDown={e => { if (e.key === ' ') e.preventDefault(); }}
                            onChange={e => { setConfirm(e.target.value); setFieldErrors(prev => ({ ...prev, confirm: undefined })); }}
                            className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition ${fieldErrors.confirm ? 'border-red-400 bg-red-50' : 'border-gray-300'}`}
                            data-testid="input-confirm-password"
                            placeholder="••••••••"
                        />
                        {fieldErrors.confirm && <p className="text-red-600 text-xs mt-1" data-testid="error-confirm">{fieldErrors.confirm}</p>}
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition shadow-md disabled:opacity-60"
                        data-testid="btn-register"
                    >
                        {loading ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <p className="text-center text-gray-500 mt-6 text-sm">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-600 font-medium hover:underline" data-testid="link-login">
                        Sign In
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterForm;
