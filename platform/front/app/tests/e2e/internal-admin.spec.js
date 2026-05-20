const { test, expect } = require('@playwright/test');

test.describe('Parcours frontend interne admin', () => {
  test.describe.configure({ mode: 'serial' });

  test('chargement dashboard interne et navigation tabs', async ({ page }) => {
    await page.goto('/interne/HomePage');

    await expect(page.getByRole('heading', { name: 'ObRail Operations' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Monitoring' })).toBeVisible();

    await page.getByRole('button', { name: 'Tests & Qualite' }).click();

    await expect(
      page.getByRole('button', { name: 'Lancer le diagnostic' })
    ).toBeVisible();

    await expect(
      page.getByRole('button', { name: 'Lancer les tests' })
    ).toBeVisible();

    await page.getByRole('button', { name: 'CI/CD' }).click();

    await expect(page.getByText(/Pipeline/i)).toBeVisible();
  });

  test('affichage erreur réseau sur overview interne', async ({ page }) => {
    await page.route('**/api/internal/overview', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'boom'
        })
      });
    });

    await page.goto('/interne/HomePage');

    await expect(
      page.getByText(/Erreur API 500 sur \/api\/internal\/overview/i)
    ).toBeVisible();

    await page.unroute('**/api/internal/overview');
  });
});