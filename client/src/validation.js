const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Mirrors the rules in server/schemas.py so users see the problem before submitting.
export function emailError(email) {
    if (!email.trim()) return 'Email is required.';
    if (/\s/.test(email)) return 'Email must not contain spaces.';
    if (!EMAIL_PATTERN.test(email)) return 'Please enter a valid email address (e.g. you@example.com).';
    return null;
}

export function passwordError(password) {
    if (!password) return 'Password is required.';
    if (/\s/.test(password)) return 'Password must not contain spaces.';
    return null;
}
