import axios from 'axios';

// Relative URL: Vite proxies /api in development, nginx does it in production.
const api = axios.create({
    baseURL: '/api',
});

export default api;

// FastAPI sends `detail` as a string for HTTPException and as a list of
// field errors for 422 validation failures.
export function apiErrorMessage(err, fallback) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail.map(e => `${e.loc?.slice(1).join('.')}: ${e.msg}`).join('; ');
    }
    return fallback;
}
