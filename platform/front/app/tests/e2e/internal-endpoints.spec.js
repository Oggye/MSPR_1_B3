const { test, expect } = require('@playwright/test');

const API_BASE_URL =
  process.env.E2E_API_URL || 'http://localhost:8000';

/**
 * Effectue une requête avec retry automatique
 */
async function fetchWithRetry(request, url, options = {}) {
  const {
    method = 'GET',
    retries = 3,
    delay = 1500,
  } = options;

  let lastResponse = null;
  let lastBody = null;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response =
        method === 'POST'
          ? await request.post(url)
          : await request.get(url);

      const rawBody = await response.text();

      console.log('='.repeat(80));
      console.log(`ATTEMPT ${attempt}/${retries}`);
      console.log(`METHOD: ${method}`);
      console.log(`URL: ${url}`);
      console.log(`STATUS: ${response.status()}`);
      console.log(`BODY: ${rawBody}`);
      console.log('='.repeat(80));

      lastResponse = response;
      lastBody = rawBody;

      // Succès
      if (response.status() === 200) {
        return {
          response,
          rawBody,
        };
      }

      // Attente avant retry
      if (attempt < retries) {
        console.log(
          `Retry dans ${delay}ms car status=${response.status()}`
        );

        await new Promise((resolve) =>
          setTimeout(resolve, delay)
        );
      }
    } catch (error) {
      console.error(
        `Erreur réseau tentative ${attempt}:`,
        error
      );

      if (attempt < retries) {
        await new Promise((resolve) =>
          setTimeout(resolve, delay)
        );
      }
    }
  }

  throw new Error(
    [
      `Erreur API après ${retries} tentatives`,
      `URL: ${url}`,
      `STATUS: ${lastResponse?.status?.()}`,
      `BODY: ${lastBody}`,
    ].join('\n')
  );
}

test.describe(
  'Endpoints internes FastAPI utilisés par le front admin',
  () => {
    test.describe.configure({
      mode: 'serial',
    });

    test(
      'GET /api/internal/overview répond et expose les blocs attendus',
      async ({ request }) => {
        test.setTimeout(120000);

        const { rawBody } = await fetchWithRetry(
          request,
          `${API_BASE_URL}/api/internal/overview`,
          {
            method: 'GET',
            retries: 5,
            delay: 2000,
          }
        );

        let body;

        try {
          body = JSON.parse(rawBody);
        } catch (error) {
          console.error('JSON invalide:', rawBody);

          throw new Error(
            `Impossible de parser le JSON:\n${rawBody}`
          );
        }

        console.log(
          'OVERVIEW JSON FORMATÉ:\n',
          JSON.stringify(body, null, 2)
        );

        // Vérification structure globale
        expect(body).toBeTruthy();

        // Vérification des blocs principaux
        expect(body).toHaveProperty('metrics');
        expect(body).toHaveProperty('prometheus');
        expect(body).toHaveProperty('grafana');
        expect(body).toHaveProperty('docker');
        expect(body).toHaveProperty('reports');

        // Vérifications supplémentaires robustes
        expect(body.metrics).toBeDefined();
        expect(body.prometheus).toBeDefined();
        expect(body.grafana).toBeDefined();
        expect(body.docker).toBeDefined();

        // Vérification status health si présent
        if (body.health) {
          expect(body.health).toHaveProperty('status');
        }
      }
    );

    test(
      'POST /api/internal/diagnostic/run répond',
      async ({ request }) => {
        test.setTimeout(120000);

        const { rawBody } = await fetchWithRetry(
          request,
          `${API_BASE_URL}/api/internal/diagnostic/run`,
          {
            method: 'POST',
            retries: 3,
            delay: 1500,
          }
        );

        let body;

        try {
          body = JSON.parse(rawBody);
        } catch (error) {
          throw new Error(
            `JSON diagnostic invalide:\n${rawBody}`
          );
        }

        console.log(
          'DIAGNOSTIC JSON:\n',
          JSON.stringify(body, null, 2)
        );

        expect(body).toHaveProperty('ran_at');
        expect(body).toHaveProperty('success');

        expect(typeof body.success).toBe('boolean');
      }
    );

    test(
      'POST /api/internal/tests/run répond',
      async ({ request }) => {
        test.setTimeout(120000);

        const { rawBody } = await fetchWithRetry(
          request,
          `${API_BASE_URL}/api/internal/tests/run`,
          {
            method: 'POST',
            retries: 3,
            delay: 1500,
          }
        );

        let body;

        try {
          body = JSON.parse(rawBody);
        } catch (error) {
          throw new Error(
            `JSON tests invalide:\n${rawBody}`
          );
        }

        console.log(
          'TESTS JSON:\n',
          JSON.stringify(body, null, 2)
        );

        expect(body).toHaveProperty('ran_at');
        expect(body).toHaveProperty('success');

        expect(typeof body.success).toBe('boolean');

        // Logs complets pytest si présents
        if (body.stdout) {
          console.log('\nPYTEST STDOUT:\n');
          console.log(body.stdout);
        }

        if (body.stderr) {
          console.error('\nPYTEST STDERR:\n');
          console.error(body.stderr);
        }
      }
    );
  }
);