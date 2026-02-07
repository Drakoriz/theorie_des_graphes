import pandas as pd
import random
import io
from typing import Tuple, List


def generer_noms_villes(n: int) -> List[str]:
    """
    Génère une liste de noms de villes uniques.
    """
    # Liste étendue de noms de villes françaises
    villes_disponibles = [
        "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg",
        "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre", "Saint-Étienne",
        "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne", "Clermont-Ferrand",
        "Le Mans", "Aix-en-Provence", "Brest", "Tours", "Amiens", "Limoges", "Annecy",
        "Perpignan", "Boulogne-Billancourt", "Metz", "Besançon", "Orléans", "Mulhouse",
        "Rouen", "Caen", "Nancy", "Argenteuil", "Montreuil", "Saint-Denis", "Roubaix",
        "Tourcoing", "Avignon", "Poitiers", "Nanterre", "Créteil", "Versailles", "Pau",
        "Courbevoie", "Vitry-sur-Seine", "Colombes", "Aulnay-sous-Bois", "Asnières-sur-Seine",
        "Rueil-Malmaison", "Antibes", "Saint-Maur-des-Fossés", "Champigny-sur-Marne", "Aubervilliers",
        "La Rochelle", "Calais", "Cannes", "Colmar", "Bourges", "Ajaccio", "Drancy"
    ]
    
    # S'assurer qu'on a assez de villes
    if n > len(villes_disponibles):
        # Ajouter des villes génériques si nécessaire
        for i in range(len(villes_disponibles), n):
            villes_disponibles.append(f"Ville_{i+1}")
    
    return random.sample(villes_disponibles, n)


def calculer_limites_aretes(nb_villes: int) -> Tuple[int, int]:
    """
    Calcule le nombre minimum et maximum d'arêtes possibles.
    """
    if nb_villes < 2:
        return 0, 0
    
    # Minimum pour un graphe connexe : n-1 arêtes (arbre)
    min_aretes = nb_villes - 1
    
    # Maximum pour un graphe complet : n*(n-1)/2 arêtes
    max_aretes = (nb_villes * (nb_villes - 1)) // 2
    
    return min_aretes, max_aretes


def generer_graphe_aleatoire(nb_villes: int, nb_aretes: int, dist_min: int = 30, dist_max: int = 200) -> pd.DataFrame:
    """
    Génère un graphe aléatoire connexe avec le nombre spécifié de villes et d'arêtes.
    
    Stratégie:
    1. Créer d'abord un arbre couvrant (n-1 arêtes) pour garantir la connexité
    2. Ajouter des arêtes supplémentaires aléatoires jusqu'à atteindre le nombre souhaité
    """
    # Générer les noms de villes
    villes = generer_noms_villes(nb_villes)
    
    # Vérifier les contraintes
    min_aretes, max_aretes = calculer_limites_aretes(nb_villes)
    nb_aretes = max(min_aretes, min(nb_aretes, max_aretes))
    
    aretes = []
    aretes_set = set()
    
    # Étape 1: Créer un arbre couvrant pour garantir la connexité
    # Utiliser une approche similaire à Prim
    villes_connectees = [villes[0]]
    villes_non_connectees = villes[1:]
    
    while villes_non_connectees:
        # Choisir une ville connectée et une non connectée
        ville_a = random.choice(villes_connectees)
        ville_b = villes_non_connectees.pop(random.randint(0, len(villes_non_connectees) - 1))
        
        distance = random.randint(dist_min, dist_max)
        
        # Normaliser l'arête (ordre alphabétique)
        u, v = sorted([ville_a, ville_b])
        aretes.append({
            "ville_a": u,
            "ville_b": v,
            "distance": distance
        })
        aretes_set.add((u, v))
        
        villes_connectees.append(ville_b)
    
    # Étape 2: Ajouter des arêtes supplémentaires si nécessaire
    aretes_restantes = nb_aretes - len(aretes)
    
    # Générer toutes les arêtes possibles
    aretes_possibles = []
    for i in range(len(villes)):
        for j in range(i + 1, len(villes)):
            u, v = sorted([villes[i], villes[j]])
            if (u, v) not in aretes_set:
                aretes_possibles.append((u, v))
    
    # Ajouter aléatoirement des arêtes supplémentaires
    if aretes_restantes > 0 and aretes_possibles:
        aretes_a_ajouter = random.sample(
            aretes_possibles, 
            min(aretes_restantes, len(aretes_possibles))
        )
        
        for u, v in aretes_a_ajouter:
            distance = random.randint(dist_min, dist_max)
            aretes.append({
                "ville_a": u,
                "ville_b": v,
                "distance": distance
            })
    
    # Créer le DataFrame
    df = pd.DataFrame(aretes)
    
    # Mélanger l'ordre des arêtes pour plus de naturel
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df


def dataframe_vers_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Convertit un DataFrame en bytes CSV pour téléchargement.
    """
    output = io.BytesIO()
    # Utiliser le séparateur point-virgule comme dans le fichier original
    df.to_csv(output, sep=';', index=False, encoding='utf-8-sig')
    return output.getvalue()


def csv_bytes_vers_dataframe(csv_bytes: bytes) -> pd.DataFrame:
    """
    Convertit des bytes CSV en DataFrame.
    """
    return pd.read_csv(io.BytesIO(csv_bytes), sep=';')


def valider_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Valide qu'un DataFrame contient les colonnes requises et des données valides.
    Vérifie également les doublons, boucles, et la connexité du graphe.
    """
    # Vérifier les colonnes requises
    colonnes_requises = {'ville_a', 'ville_b', 'distance'}
    colonnes_presentes = set(df.columns)
    
    if not colonnes_requises.issubset(colonnes_presentes):
        colonnes_manquantes = colonnes_requises - colonnes_presentes
        return False, f"Colonnes manquantes : {', '.join(colonnes_manquantes)}"
    
    # Vérifier qu'il y a des données
    if len(df) == 0:
        return False, "Le fichier ne contient aucune arête"
    
    # Nettoyer les espaces dans les noms de villes
    df = df.copy()
    df['ville_a'] = df['ville_a'].astype(str).str.strip()
    df['ville_b'] = df['ville_b'].astype(str).str.strip()
    
    # Vérifier qu'il n'y a pas de valeurs manquantes dans les villes
    if df['ville_a'].isna().any() or df['ville_b'].isna().any():
        return False, "Certains noms de villes sont manquants"
    
    # Vérifier qu'il n'y a pas de villes vides
    if (df['ville_a'] == '').any() or (df['ville_b'] == '').any():
        return False, "Certains noms de villes sont vides"
    
    # Vérifier les boucles (arête d'une ville vers elle-même)
    boucles = df[df['ville_a'] == df['ville_b']]
    if len(boucles) > 0:
        villes_boucles = boucles['ville_a'].unique()
        return False, f"Boucles détectées (ville vers elle-même) : {', '.join(villes_boucles[:3])}{'...' if len(villes_boucles) > 3 else ''}"
    
    # Vérifier que les distances sont numériques et positives
    try:
        distances = pd.to_numeric(df['distance'].astype(str).str.strip(), errors='coerce')
        if distances.isna().any():
            return False, "Certaines distances ne sont pas des nombres valides"
        if (distances <= 0).any():
            return False, "Toutes les distances doivent être strictement positives"
        if (distances > 10000).any():
            return False, "Certaines distances sont anormalement élevées (> 10000 km)"
    except Exception as e:
        return False, f"Erreur lors de la validation des distances : {str(e)}"
    
    # Vérifier les doublons (même arête présente plusieurs fois)
    aretes_normalisees = []
    for _, row in df.iterrows():
        u, v = row['ville_a'], row['ville_b']
        # Normaliser l'arête (ordre alphabétique)
        arete = tuple(sorted([u, v]))
        aretes_normalisees.append(arete)
    
    # Compter les doublons
    from collections import Counter
    compteur = Counter(aretes_normalisees)
    doublons = [(arete, count) for arete, count in compteur.items() if count > 1]
    
    if doublons:
        exemple_doublon = doublons[0][0]
        return False, f"Arêtes en doublon détectées : {exemple_doublon[0]} ↔ {exemple_doublon[1]} (apparaît {doublons[0][1]} fois)"
    
    # Vérifier la connexité du graphe (tous les sommets sont accessibles)
    graphe = dataframe_vers_graphe(df)
    if not verifier_connexite(graphe):
        return False, "Le graphe n'est pas connexe (certaines villes sont isolées)"
    
    # Vérifier qu'il y a au moins 2 villes
    nb_villes = len(graphe)
    if nb_villes < 2:
        return False, "Le graphe doit contenir au moins 2 villes"
    
    return True, "CSV valide"


def verifier_connexite(graphe: dict) -> bool:
    """
    Vérifie si le graphe est connexe (tous les sommets sont accessibles).
    """
    if not graphe:
        return False
    
    # BFS pour vérifier la connexité
    sommets = set(graphe.keys())
    depart = next(iter(sommets))
    visites = {depart}
    file = [depart]
    
    while file:
        courant = file.pop(0)
        for voisin in graphe[courant].keys():
            if voisin not in visites:
                visites.add(voisin)
                file.append(voisin)
    
    return len(visites) == len(sommets)


def charger_template_defaut() -> pd.DataFrame:
    """
    Charge le template par défaut (villes.csv).
    """
    try:
        df = pd.read_csv("villes.csv", sep=";")
        # Nettoyer les espaces dans les colonnes de texte
        df['ville_a'] = df['ville_a'].str.strip()
        df['ville_b'] = df['ville_b'].str.strip()
        # Convertir la distance en numérique en gérant les espaces
        df['distance'] = pd.to_numeric(df['distance'].astype(str).str.strip(), errors='coerce')
        return df
    except FileNotFoundError:
        # Si le fichier n'existe pas, créer un template minimal
        return pd.DataFrame({
            'ville_a': ['Paris', 'Paris', 'Lyon'],
            'ville_b': ['Lyon', 'Marseille', 'Marseille'],
            'distance': [150, 200, 100]
        })


def dataframe_vers_graphe(df: pd.DataFrame) -> dict:
    """
    Convertit un DataFrame en dictionnaire de graphe (format utilisé par l'application).
    """
    graphe = {}
    for _, ligne in df.iterrows():
        u = str(ligne["ville_a"]).strip()
        v = str(ligne["ville_b"]).strip()
        poids = float(ligne["distance"])
        
        graphe.setdefault(u, {})[v] = poids
        graphe.setdefault(v, {})[u] = poids
    
    return graphe


def obtenir_statistiques_graphe(df: pd.DataFrame) -> dict:
    """
    Calcule des statistiques sur le graphe.
    """
    # Extraire toutes les villes uniques
    villes = set(df['ville_a'].unique()) | set(df['ville_b'].unique())
    
    # Calculer les statistiques
    stats = {
        'nb_villes': len(villes),
        'nb_aretes': len(df),
        'distance_min': df['distance'].min(),
        'distance_max': df['distance'].max(),
        'distance_moyenne': df['distance'].mean(),
        'distance_totale': df['distance'].sum()
    }
    
    # Calculer le degré moyen
    graphe = dataframe_vers_graphe(df)
    degres = [len(voisins) for voisins in graphe.values()]
    stats['degre_moyen'] = sum(degres) / len(degres) if degres else 0
    
    return stats


def graphe_oriente_vers_dataframe(graphe_oriente: dict) -> pd.DataFrame:
    """
    Convertit un graphe orienté en DataFrame CSV.
    
    Args:
        graphe_oriente: Dictionnaire du graphe orienté
    
    Returns:
        pd.DataFrame: DataFrame avec colonnes ville_a, ville_b, distance
    """
    aretes = []
    
    for u in graphe_oriente:
        for v, poids in graphe_oriente[u].items():
            aretes.append({
                'ville_a': u,
                'ville_b': v,
                'distance': poids
            })
    
    return pd.DataFrame(aretes)