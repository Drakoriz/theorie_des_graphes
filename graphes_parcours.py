from collections import deque


def init_bfs(graphe, depart):
    """
    Initialise l'état du parcours en largeur (BFS).
    """
    return {
        "visites": [],  # Liste pour conserver l'ordre chronologique
        "file": deque([depart]),
        "courant": None,
        "termine": False
    }


def etape_bfs(graphe, etat, session_state):
    """
    Exécute une étape du parcours en largeur (BFS).
    
    Le BFS explore le graphe niveau par niveau :
    1. Défiler le prochain sommet de la file
    2. Le marquer comme visité
    3. Ajouter tous ses voisins non visités à la file
    """
    if not etat["file"]:
        etat["termine"] = True
        return etat
    
    # Défiler le prochain sommet à explorer
    courant = etat["file"].popleft()
    etat["courant"] = courant
    
    # Marquer comme visité (conserver l'ordre chronologique)
    if courant not in etat["visites"]:
        etat["visites"].append(courant)
    
    # Explorer les voisins dans l'ordre alphabétique
    for voisin in sorted(graphe[courant].keys()):
        if voisin not in etat["visites"] and voisin not in etat["file"]:
            etat["file"].append(voisin)
    
    # Enregistrer l'étape dans l'historique (ordre chronologique)
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "courant": courant,
        "file": list(etat["file"]),
        "visites": list(etat["visites"])  # Ordre chronologique conservé
    }
    
    session_state.historique.append(info_etape)
    return etat


def init_dfs(graphe, depart):
    """
    Initialise l'état du parcours en profondeur (DFS).
    """
    return {
        "visites": [],  # Liste pour conserver l'ordre chronologique
        "pile": [depart],
        "courant": None,
        "termine": False
    }


def etape_dfs(graphe, etat, session_state):
    """
    Exécute une étape du parcours en profondeur (DFS).
    
    Le DFS explore le graphe en profondeur :
    1. Dépiler le sommet au sommet de la pile
    2. Le marquer comme visité
    3. Empiler tous ses voisins non visités
    """
    if not etat["pile"]:
        etat["termine"] = True
        return etat
    
    # Dépiler le sommet à explorer
    courant = etat["pile"].pop()
    etat["courant"] = courant
    
    # Marquer comme visité seulement maintenant (conserver l'ordre chronologique)
    if courant not in etat["visites"]:
        etat["visites"].append(courant)
    
    # Ajouter les voisins non visités et non déjà dans la pile
    # reversed() pour maintenir l'ordre alphabétique avec une pile (LIFO)
    for voisin in reversed(sorted(list(graphe[courant].keys()))):
        if voisin not in etat["visites"] and voisin not in etat["pile"]:
            etat["pile"].append(voisin)
    
    # Enregistrer l'étape dans l'historique (ordre chronologique)
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "courant": courant,
        "pile": list(etat["pile"]),
        "visites": list(etat["visites"])  # Ordre chronologique conservé
    }
    
    session_state.historique.append(info_etape)
    
    return etat