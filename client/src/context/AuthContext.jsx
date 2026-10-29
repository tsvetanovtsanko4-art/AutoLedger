import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(() => localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    // Only a stored token needs verifying, so there is nothing to wait for without one.
    const [loading, setLoading] = useState(() => Boolean(localStorage.getItem('token')));

    const logout = () => {
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
        setToken(null);
        setUser(null);
    };

    useEffect(() => {
        if (!token) return;
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        api.get('/me')
            .then(res => setUser(res.data))
            .catch(logout)
            .finally(() => setLoading(false));
    }, [token]);

    const login = async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        const res = await api.post('/auth/login', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        const newToken = res.data.access_token;
        localStorage.setItem('token', newToken);
        api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        setToken(newToken);
        const meRes = await api.get('/me');
        setUser(meRes.data);
    };

    const register = async (email, password) => {
        await api.post('/auth/register', { email, password });
        await login(email, password);
    };

    return (
        <AuthContext.Provider value={{ token, user, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
