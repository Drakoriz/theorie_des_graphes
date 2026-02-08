from collections import deque


def init_bfs(graphe, depart):
    """
    Initialise l'état du parcours en largeur (BFS).
    """
    return {
        "visites": [],  # Liste pour conserver l'ordre chronologique (affichage)
        "visites_set": set(),  # Set pour vérifications rapides O(1)
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
    
    Le parcours s'arrête quand tous les sommets sont visités OU la file est vide.
    """
    # Arrêt si la file est vide OU tous les sommets sont visités
    if not etat["file"] or len(etat["visites"]) >= len(graphe):
        etat["termine"] = True
        return etat
    
    # Défiler le prochain sommet à explorer
    courant = etat["file"].popleft()
    etat["courant"] = courant
    
    # Marquer comme visité (conserver l'ordre chronologique + set pour performance)
    if courant not in etat["visites_set"]:
        etat["visites"].append(courant)
        etat["visites_set"].add(courant)
    
    # Explorer les voisins dans l'ordre alphabétique
    for voisin in sorted(graphe[courant].keys()):
        if voisin not in etat["visites_set"] and voisin not in etat["file"]:
            etat["file"].append(voisin)
    
    # Enregistrer l'étape dans l'historique (ordre chronologique)
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "courant": courant,
        "file": list(etat["file"]),
        "visites": list(etat["visites"])  # Ordre chronologique conservé
    }
    
    session_state.historique.append(info_etape)
    # Note: Le compteur est incrémenté dans main.py, pas ici
    return etat


def init_dfs(graphe, depart):
    """
    Initialise l'état du parcours en profondeur (DFS).
    """
    return {
        "visites": [],  # Liste pour conserver l'ordre chronologique (affichage)
        "visites_set": set(),  # Set pour vérifications rapides O(1)
        "pile": [depart],
        "courant": None,
        "termine": False
    }


def etape_dfs(graphe, etat, session_state):
    """
    Exécute une étape du parcours en profondeur (DFS) itératif.
    
    Le DFS explore le graphe en profondeur :
    1. Dépiler le prochain sommet de la pile
    2. Si pas encore visité, le marquer comme visité
    3. Ajouter tous ses voisins non visités à la pile
    
    Le parcours s'arrête quand tous les sommets sont visités OU la pile est vide.
    
    Note: Les doublons dans la pile sont autorisés (comportement DFS classique).
    Seuls les sommets non encore visités sont colorés en orange dans l'affichage.
    """
    # Arrêt si la pile est vide OU tous les sommets sont visités
    if not etat["pile"] or len(etat["visites"]) >= len(graphe):
        etat["termine"] = True
        return etat
    
    # Dépiler le prochain sommet à explorer
    courant = etat["pile"].pop()
    etat["courant"] = courant
    
    # Si déjà visité, passer à l'étape suivante sans enregistrer
    if courant in etat["visites_set"]:
        return etat
    
    # Marquer comme visité (conserver l'ordre chronologique + set pour performance)
    etat["visites"].append(courant)
    etat["visites_set"].add(courant)
    
    # Explorer les voisins dans l'ordre alphabétique inverse
    # (reverse=True car on empile, donc le dernier empilé sera le premier dépilé)
    for voisin in sorted(graphe[courant].keys(), reverse=True):
        if voisin not in etat["visites_set"]:
            etat["pile"].append(voisin)
    
    # Enregistrer l'étape dans l'historique (ordre chronologique)
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "courant": courant,
        "pile": list(etat["pile"]),
        "visites": list(etat["visites"])  # Ordre chronologique conservé
    }
    
    session_state.historique.append(info_etape)
    # Note: Le compteur est incrémenté dans main.py, pas ici
    return etat