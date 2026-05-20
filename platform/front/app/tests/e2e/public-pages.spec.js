const { test, expect } = require('@playwright/test');

test.describe('Parcours frontend externe', () => {
  async function openMobileMenuIfNeeded(page) {
    const menuButton = page.getByRole('button', { name: /☰/ });
    if (await menuButton.isVisible()) {
      await menuButton.click();
    }
  }

  test('navigation entre toutes les pages externes obligatoires', async ({ page }) => {
    await page.goto('/externe/HomePage');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    await openMobileMenuIfNeeded(page);
    await page.getByRole('link', { name: /Trajets/i }).click();
    await expect(page).toHaveURL(/\/externe\/Trajets$/);
    await expect(page.getByRole('heading', { name: /Recherche d'itinéraires ferroviaires/i })).toBeVisible();

    await openMobileMenuIfNeeded(page);
    await page.getByRole('link', { name: /Carte/i }).click();
    await expect(page).toHaveURL(/\/externe\/Map$/);

    // Attendre que la carte soit chargée avant de vérifier le titre
    await expect(page.locator('.map-container')).toBeVisible();
    await expect(page.getByRole('heading', { name: /Carte.*Trains/i })).toBeVisible();

    await openMobileMenuIfNeeded(page);
    await page.getByRole('link', { name: /Statistiques/i }).click();
    await expect(page).toHaveURL(/\/externe\/Statistique$/);
    await expect(page.getByRole('heading', { name: /Tableau de Bord Statistique/i })).toBeVisible();

    await openMobileMenuIfNeeded(page);
    await page.getByRole('link', { name: /Opérateurs/i }).click();
    await expect(page).toHaveURL(/\/externe\/Operateur$/);
    await expect(page.getByRole('heading', { name: /Opérateurs Ferroviaires/i })).toBeVisible();
  });

  test('page trajets: filtres + état vide utilisateur', async ({ page }) => {
    await page.goto('/externe/Trajets');
    await expect(page.getByRole('heading', { name: /Recherche d'itinéraires ferroviaires/i })).toBeVisible();

    await page.getByPlaceholder('Ecrire un operateur...').fill('this_operator_does_not_exist');
    await expect(page.getByText('Aucun trajet trouvé')).toBeVisible();
  });

  test('page map: filtres et reset', async ({ page }) => {
    await page.goto('/externe/Map');

    // Attendre que la carte soit chargée avant de vérifier le titre et les filtres
    await expect(page.locator('.map-container')).toBeVisible();
    await expect(page.getByRole('heading', { name: /Carte.*Trains/i })).toBeVisible();
    await expect(page.locator('.filter-select')).toHaveCount(3);

    await page.locator('.filter-select').first().selectOption('night');
    await page.getByRole('button', { name: /Réinitialiser/i }).click();
    await expect(page.getByRole('heading', { name: /Nombre de trains par pays/i })).toBeVisible();
  });

  test('page statistiques: sections analytiques visibles', async ({ page }) => {
    await page.goto('/externe/Statistique');
    await expect(page.getByRole('heading', { name: /Tableau de Bord Statistique/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Comparaison Trains de Jour vs Nuit/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /Classement CO₂ par passager/i })).toBeVisible();
  });

  test('page opérateurs: sélection d’un opérateur et affichage détails', async ({ page }) => {
    await page.goto('/externe/Operateur');
    await expect(page.getByRole('heading', { name: /Opérateurs Ferroviaires/i })).toBeVisible();

    const rows = page.locator('tbody tr');
    const count = await rows.count();
    test.skip(count === 0, 'Aucun opérateur disponible dans l’environnement de test');

    await rows.first().click();
    await expect(page.getByText(/Opérateur ferroviaire européen/i)).toBeVisible();
    await expect(page.getByText(/INDICATEURS DE PERFORMANCE/i)).toBeVisible();
  });
});