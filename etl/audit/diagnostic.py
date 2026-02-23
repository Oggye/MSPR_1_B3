# =========================================================
# diagnostic.py - Version avec aperçu
# =========================================================

import pandas as pd
from pathlib import Path
import glob

# Dossiers à analyser
DOSSIERS = {
    "back_on_track": "data/raw/back_on_track/*.csv",
    "eurostat": "data/raw/eurostat/*.csv",
    "emission_co2": "data/raw/emission_co2/*.csv",
    "gtfs_fr": "data/raw/gtfs_fr/*.csv",
    "gtfs_ch": "data/raw/gtfs_ch/*.csv",
    "gtfs_de": "data/raw/gtfs_de/*.csv",
}

def analyser_fichier(chemin_fichier):
    """Analyse un fichier sans tout charger en mémoire"""
    try:
        nom_fichier = Path(chemin_fichier).name
        taille_kb = Path(chemin_fichier).stat().st_size / 1024
        
        # Lire seulement les premières lignes pour les infos
        if chemin_fichier.endswith('.tsv'):
            sep = '\t'
        else:
            sep = ','
        
        # Méthode 1: Essayer de lire les premières lignes
        try:
            # Lire juste l'en-tête et quelques lignes
            df_sample = pd.read_csv(chemin_fichier, sep=sep, nrows=5)
            nb_colonnes = len(df_sample.columns)
            
            # Compter les lignes de manière optimisée
            with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
                nb_lignes = sum(1 for _ in f) - 1  # -1 pour l'en-tête
            
            # Lire les 10 premières lignes pour l'aperçu
            df_preview = pd.read_csv(chemin_fichier, sep=sep, nrows=10)
            preview = df_preview
            
            return {
                'nom': nom_fichier,
                'lignes': nb_lignes,
                'colonnes': nb_colonnes,
                'taille_kb': taille_kb,
                'preview': preview,
                'erreur': None
            }
            
        except pd.errors.ParserError as e:
            # Méthode 2: Si échec, lire en mode texte
            with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
                lignes = [next(f) for _ in range(11)]  # 10 lignes + en-tête
            
            # Estimer les colonnes à partir de la première ligne
            premiere_ligne = lignes[0].strip()
            if sep == ',':
                nb_colonnes = len(premiere_ligne.split(','))
            else:
                nb_colonnes = len(premiere_ligne.split('\t'))
            
            with open(chemin_fichier, 'r', encoding='utf-8', errors='ignore') as f:
                nb_lignes = sum(1 for _ in f) - 1
            
            # Créer un aperçu texte
            preview_text = "\n".join([f"      Ligne {i}: {ligne[:100].strip()}" 
                                     for i, ligne in enumerate(lignes[:11], 1)])
            
            return {
                'nom': nom_fichier,
                'lignes': nb_lignes,
                'colonnes': nb_colonnes,
                'taille_kb': taille_kb,
                'preview': preview_text,
                'erreur': f'Format spécial: {str(e)[:30]}'
            }
            
    except Exception as e:
        return {
            'nom': Path(chemin_fichier).name,
            'lignes': 0,
            'colonnes': 0,
            'taille_kb': Path(chemin_fichier).stat().st_size / 1024,
            'preview': None,
            'erreur': str(e)[:50]
        }

def afficher_resume_avec_apercu():
    """Affiche un résumé avec aperçu des 10 premières lignes"""
    print("📊 RÉSUMÉ DES DONNÉES AVEC APERÇU")
    print("=" * 60)
    
    total_lignes = 0
    total_fichiers = 0
    
    for nom, chemin in DOSSIERS.items():
        fichiers = glob.glob(chemin)
        
        print(f"\n{'='*60}")
        print(f"📁 {nom.upper()}:")
        print(f"{'='*60}")
        
        if not fichiers:
            print("   Aucun fichier")
            continue
            
        for f in fichiers:
            print(f"\n📄 Fichier: {Path(f).name}")
            print(f"📁 Chemin: {f}")
            
            resultat = analyser_fichier(f)
            total_fichiers += 1
            
            if resultat['erreur']:
                print(f"   ⚠️  Erreur: {resultat['erreur']}")
                print(f"   📏 Taille: {resultat['taille_kb']:.1f} KB")
            else:
                print(f"   ✅ Lignes: {resultat['lignes']:,}")
                print(f"   🗂️  Colonnes: {resultat['colonnes']}")
                print(f"   📏 Taille: {resultat['taille_kb']:.1f} KB")
                total_lignes += resultat['lignes']
                
                # Afficher les 10 premières lignes
                print(f"\n   👀 10 PREMIÈRES LIGNES:")
                print(f"   {'-'*40}")
                
                if isinstance(resultat['preview'], pd.DataFrame):
                    # Afficher le DataFrame
                    pd.set_option('display.max_columns', None)
                    pd.set_option('display.width', 120)
                    print(resultat['preview'].to_string())
                elif isinstance(resultat['preview'], str):
                    # Afficher le texte brut
                    print(resultat['preview'])
                else:
                    print("   (Aperçu non disponible)")
                
                print(f"   {'-'*40}")
    
    print(f"\n{'='*60}")
    print(f"📈 SYNTHÈSE:")
    print(f"   • {total_fichiers} fichiers analysés")
    print(f"   • {total_lignes:,} lignes totales")
    print("=" * 60)

def afficher_resume_rapide():
    """Affiche seulement un résumé rapide"""
    print("📋 RÉSUMÉ RAPIDE")
    print("=" * 50)
    
    total_lignes = 0
    total_fichiers = 0
    
    for nom, chemin in DOSSIERS.items():
        fichiers = glob.glob(chemin)
        
        print(f"\n📁 {nom}:")
        if not fichiers:
            print("   Aucun fichier")
            continue
            
        for f in fichiers:
            resultat = analyser_fichier(f)
            total_fichiers += 1
            
            if resultat['erreur']:
                print(f"   ⚠️ {resultat['nom']}")
                print(f"      Erreur: {resultat['erreur']}")
            else:
                print(f"   ✓ {resultat['nom']}")
                print(f"      Lignes: {resultat['lignes']:,}")
                print(f"      Colonnes: {resultat['colonnes']}")
                total_lignes += resultat['lignes']
    
    print(f"\n{'='*50}")
    print(f"📈 TOTAL: {total_fichiers} fichiers, {total_lignes:,} lignes")
    print("=" * 50)

if __name__ == "__main__":
    print("🔧 UTILISATION :")
    print("   python diagnostic.py          # Résumé avec aperçu complet")
    print("   python diagnostic.py --rapide # Résumé rapide seulement")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--rapide":
        afficher_resume_rapide()
    else:
        afficher_resume_avec_apercu()