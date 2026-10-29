import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiErrorMessage } from '../api';
import { useAuth } from '../context/AuthContext';
import { emailError, passwordError } from '../validation';

const LoginForm = () => {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [fieldErrors, setFieldErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        const errors = {};
        const emailProblem = emailError(email);
        if (emailProblem) errors.email = emailProblem;
        const passwordProblem = passwordError(password);
        if (passwordProblem) errors.password = passwordProblem;

        if (Object.keys(errors).length > 0) {
            setFieldErrors(errors);
            return;
        }

        setFieldErrors({});
        setLoading(true);
        try {
            await login(email.trim(), password);
            navigate('/home');
        } catch (err) {
            setError(apiErrorMessage(err, 'Login failed. Check your credentials.'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 to-slate-900 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
                <div className="text-center mb-8">
                    <div className="text-5xl mb-3">🚗</div>
                    <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
                    <p className="text-gray-500 mt-2">Sign in to your Car Tracker account</p>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm" data-testid="login-error">
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
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 text-white font-semibold py-3 rounded-xl hover:bg-blue-700 transition shadow-md disabled:opacity-60"
                        data-testid="btn-login"
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <p className="text-center text-gray-500 mt-6 text-sm">
                    Don't have an account?{' '}
                    <Link to="/register" className="text-blue-600 font-medium hover:underline" data-testid="link-register">
                        Register
                    </Link>
                </p>
                <p className="text-center mt-2">
                    <Link to="/" className="text-gray-400 text-xs hover:text-gray-600">← Back to public dashboard</Link>
                </p>
            </div>
        </div>
    );
};

export default LoginForm;
