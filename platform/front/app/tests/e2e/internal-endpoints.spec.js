const { test, expect } = require('@playwright/test');

const API_BASE_URL = process.env.E2E_API_URL || 'http://localhost:8000';

test.describe('Endpoints internes FastAPI utilisés par le front admin', () => {

  test('GET /api/internal/overview répond et expose les blocs attendus', async ({ request }, testInfo) => {
    // Timeout plus large pour éviter les faux négatifs CI/CD
    test.setTimeout(30000);

    const response = await request.get(
      `${API_BASE_URL}/api/internal/overview`,
      {
        timeout: 20000,
        failOnStatusCode: false
      }
    );

    // Logs utiles pour debug CI
    console.log('STATUS:', response.status());
    console.log('URL:', response.url());

    const rawBody = await response.text();

    console.log('BODY:', rawBody);

    // Vérification explicite du status HTTP
    expect(
      response.status(),
      `Erreur API overview : ${rawBody}`
    ).toBe(200);

    // Parse JSON sécurisé
    let body;

    try {
      body = JSON.parse(rawBody);
    } catch (error) {
      throw new Error(
        `Réponse non JSON reçue sur /api/internal/overview\n\n${rawBody}`
      );
    }

    // Vérification structure API
    expect(body).toHaveProperty('metrics');
    expect(body).toHaveProperty('prometheus');
    expect(body).toHaveProperty('grafana');
    expect(body).toHaveProperty('docker');
    expect(body).toHaveProperty('reports');
  });

  test('POST /api/internal/diagnostic/run répond', async ({ request }) => {
    test.setTimeout(90000);

    const response = await request.post(
      `${API_BASE_URL}/api/internal/diagnostic/run`,
      {
        timeout: 60000,
        failOnStatusCode: false
      }
    );

    console.log('DIAGNOSTIC STATUS:', response.status());

    const rawBody = await response.text();

    console.log('DIAGNOSTIC BODY:', rawBody);

    expect(
      response.status(),
      `Erreur diagnostic : ${rawBody}`
    ).toBe(200);

    let body;

    try {
      body = JSON.parse(rawBody);
    } catch (error) {
      throw new Error(
        `Réponse non JSON reçue sur /api/internal/diagnostic/run\n\n${rawBody}`
      );
    }

    expect(body).toHaveProperty('ran_at');
    expect(body).toHaveProperty('success');
  });

  test('POST /api/internal/tests/run répond', async ({ request }) => {
    test.setTimeout(90000);

    const response = await request.post(
      `${API_BASE_URL}/api/internal/tests/run`,
      {
        timeout: 60000,
        failOnStatusCode: false
      }
    );

    console.log('TESTS STATUS:', response.status());

    const rawBody = await response.text();

    console.log('TESTS BODY:', rawBody);

    expect(
      response.status(),
      `Erreur tests/run : ${rawBody}`
    ).toBe(200);

    let body;

    try {
      body = JSON.parse(rawBody);
    } catch (error) {
      throw new Error(
        `Réponse non JSON reçue sur /api/internal/tests/run\n\n${rawBody}`
      );
    }

    expect(body).toHaveProperty('ran_at');
    expect(body).toHaveProperty('success');
  });

});