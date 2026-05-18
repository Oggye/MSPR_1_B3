const { test, expect } = require('@playwright/test');

const API_BASE_URL = process.env.E2E_API_URL || 'http://localhost:8000';

test.describe('Endpoints internes FastAPI utilisés par le front admin', () => {
  test('GET /api/internal/overview répond et expose les blocs attendus', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/internal/overview`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty('metrics');
    expect(body).toHaveProperty('prometheus');
    expect(body).toHaveProperty('grafana');
    expect(body).toHaveProperty('docker');
    expect(body).toHaveProperty('reports');
  });

  test('POST /api/internal/diagnostic/run répond', async ({ request }) => {
    test.setTimeout(90000);
    const response = await request.post(`${API_BASE_URL}/api/internal/diagnostic/run`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty('ran_at');
    expect(body).toHaveProperty('success');
  });

  test('POST /api/internal/tests/run répond', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/internal/tests/run`);
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toHaveProperty('ran_at');
    expect(body).toHaveProperty('success');
  });
});
