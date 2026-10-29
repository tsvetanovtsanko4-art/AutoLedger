import { defineConfig, devices } from '@playwright/test';
import process from 'node:process';

// Starts a throwaway API on SQLite plus the Vite dev server, then drives a real browser.
// PYTHON points at the interpreter that has server/requirements.txt installed.
const python = process.env.PYTHON || 'python';
const apiPort = 8001;
const webPort = 5174;

export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: Boolean(process.env.CI),
    retries: process.env.CI ? 1 : 0,
    reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
    use: {
        baseURL: `http://localhost:${webPort}`,
        trace: 'retain-on-failure',
    },
    projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
    webServer: [
        {
            command: `${python} -m alembic -c server/alembic.ini upgrade head && ${python} -m uvicorn server.main:app --port ${apiPort}`,
            cwd: '..',
            url: `http://localhost:${apiPort}/api/health`,
            env: {
                DATABASE_URL: 'sqlite:///./e2e.db',
                SECRET_KEY: 'e2e-secret-key-not-used-anywhere-else',
            },
            reuseExistingServer: !process.env.CI,
        },
        {
            command: `npx vite --port ${webPort} --strictPort`,
            url: `http://localhost:${webPort}`,
            env: { VITE_HTTPS: 'false', VITE_API_TARGET: `http://localhost:${apiPort}` },
            reuseExistingServer: !process.env.CI,
        },
    ],
});
