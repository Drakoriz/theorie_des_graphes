import networkx as nx
import matplotlib.pyplot as plt
import heapq
def dijkstra(graphe, depart, arrivee):
    """
    Algorithme de Dijkstra pour trouver le plus court chemin entre deux sommets.
    Fonctionne uniquement avec des poids positifs.
    """
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {sommet: None for sommet in graphe}
    visites = set()
    file_priorite = [(0, depart)]
    etapes = []
    
    etapes.append({
        "sommet": depart,
        "distance": 0,
        "visites": set(),
        "distances": distances.copy(),
        "raison": "Initialisation"
    })
    
    while file_priorite:
        dist_courante, sommet_courant = heapq.heappop(file_priorite)
        
        if sommet_courant in visites:
            continue
        
        visites.add(sommet_courant)
        
        etapes.append({
            "sommet": sommet_courant,
            "distance": dist_courante,
            "visites": visites.copy(),
            "distances": distances.copy(),
            "raison": f"Visite de {sommet_courant} (distance: {dist_courante:.0f})"
        })
        
        # Si on a atteint l'arrivée, on peut arrêter
        if sommet_courant == arrivee:
            break
        
        # Relaxation des arêtes
        for voisin, poids in graphe[sommet_courant].items():
            if voisin not in visites:
                nouvelle_distance = dist_courante + poids
                if nouvelle_distance < distances[voisin]:
                    distances[voisin] = nouvelle_distance
                    predecesseurs[voisin] = sommet_courant
                    heapq.heappush(file_priorite, (nouvelle_distance, voisin))
    
    # Reconstruction du chemin
    chemin = []
    sommet = arrivee
    while sommet is not None:
        chemin.append(sommet)
        sommet = predecesseurs[sommet]
    chemin.reverse()
    
    # Si le premier élément n'est pas le départ, il n'y a pas de chemin
    if chemin[0] != depart:
        return float('inf'), [], etapes
    
    return distances[arrivee], chemin, etapes


def init_dijkstra(graphe, depart, arrivee):
    """Initialise l'état de l'algorithme de Dijkstra.
    """
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    
    return {
        "depart": depart,
        "arrivee": arrivee,
        "distances": distances,
        "predecesseurs": {sommet: None for sommet in graphe},
        "visites": [],  # Liste pour conserver l'ordre chronologique
        "file_priorite": [(0, depart)],
        "sommet_courant": None,
        "chemin_trouve": [],
        "termine": False
    }


def etape_dijkstra(graphe, etat, session_state):
    """Exécute une étape de l'algorithme de Dijkstra.
    """
    if not etat["file_priorite"] or etat["termine"]:
        etat["termine"] = True
        return etat
    
    # Extraire le sommet avec la plus petite distance
    while etat["file_priorite"]:
        dist_courante, sommet_courant = heapq.heappop(etat["file_priorite"])
        
        if sommet_courant not in etat["visites"]:
            break
    else:
        etat["termine"] = True
        return etat
    
    etat["sommet_courant"] = sommet_courant
    etat["visites"].append(sommet_courant)  # Ajouter à la liste dans l'ordre chronologique
    
    # Si on a atteint l'arrivée, reconstruire le chemin
    if sommet_courant == etat["arrivee"]:
        chemin = []
        sommet = etat["arrivee"]
        while sommet is not None:
            chemin.append(sommet)
            sommet = etat["predecesseurs"][sommet]
        chemin.reverse()
        etat["chemin_trouve"] = chemin
        etat["termine"] = True
    else:
        # Relaxation des arêtes
        for voisin, poids in graphe[sommet_courant].items():
            if voisin not in etat["visites"]:
                nouvelle_distance = dist_courante + poids
                if nouvelle_distance < etat["distances"][voisin]:
                    etat["distances"][voisin] = nouvelle_distance
                    etat["predecesseurs"][voisin] = sommet_courant
                    heapq.heappush(etat["file_priorite"], (nouvelle_distance, voisin))
    
    # Enregistrer l'étape (ordre chronologique conservé)
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "sommet": sommet_courant,
        "distance": dist_courante,
        "visites": list(etat["visites"]),  # Ordre chronologique conservé
        "distances": {k: (f"{v:.0f}" if v != float('inf') else "∞") for k, v in etat["distances"].items()}
    }
    session_state.historique.append(info_etape)
    
    return etat


def dessiner_graphe_dijkstra(graphe, visites, sommet_courant, chemin=None, depart=None, arrivee=None):
    """
    Dessine le graphe pour l'algorithme de Dijkstra.
    """
    G = nx.Graph()
    for u in graphe:
        for v, poids in graphe[u].items():
            G.add_edge(u, v, weight=poids)

    pos = nx.spring_layout(G, weight="weight", seed=42, k=1.2)
    fig, ax = plt.subplots(figsize=(6, 5))

    # Dessiner toutes les arêtes
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.4)
    
    # Dessiner le chemin trouvé en vert
    if chemin and len(chemin) > 1:
        aretes_chemin = [(chemin[i], chemin[i+1]) for i in range(len(chemin)-1)]
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=aretes_chemin,
            edge_color='#13C266',
            width=3,
            alpha=1.0
        )
    
    # Couleurs des nœuds
    couleurs_noeuds = []
    for noeud in G.nodes():
        if noeud == sommet_courant:
            couleurs_noeuds.append("#B0152A")  # Rouge - sommet courant
        elif noeud == depart:
            couleurs_noeuds.append("#007AFF")  # Bleu - départ
        elif noeud == arrivee:
            couleurs_noeuds.append("#FF2D55")  # Rose - arrivée
        elif noeud in visites:
            couleurs_noeuds.append("#13C266")  # Vert - visité
        else:
            couleurs_noeuds.append("white")    # Blanc - non visité
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=couleurs_noeuds,
        node_size=500,
        edgecolors="black",
        linewidths=2
    )
    
    # Labels des nœuds
    nx.draw_networkx_labels(G, pos, ax=ax, font_weight="bold", font_size=8)
    
    # Poids des arêtes
    etiquettes_aretes = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G, pos, ax=ax,
        edge_labels=etiquettes_aretes,
        font_size=6,
        label_pos=0.3
    )

    ax.axis("off")
    fig.tight_layout()
    return fig


def init_bellman_ford(graphe, depart):
    """
    Initialise l'état de l'algorithme de Bellman-Ford.
    
    Args:
        graphe: Dictionnaire de graphe (peut contenir des poids négatifs)
        depart: Sommet de départ
    
    Returns:
        dict: État initial de l'algorithme
    """
    sommets = list(graphe.keys())
    distances = {sommet: float('inf') for sommet in sommets}
    distances[depart] = 0
    predecesseurs = {sommet: None for sommet in sommets}
    
    # Extraire toutes les arêtes (graphe orienté)
    aretes = []
    for u in graphe:
        for v, poids in graphe[u].items():
            aretes.append((u, v, poids))
    
    return {
        "depart": depart,
        "distances": distances,
        "predecesseurs": predecesseurs,
        "aretes": aretes,
        "iteration_courante": 0,
        "nb_iterations_max": len(sommets) - 1,
        "aretes_relaxees": [],  # Liste des arêtes relaxées à cette itération
        "cycle_negatif": False,
        "termine": False
    }


def etape_bellman_ford(graphe, etat, session_state):
    """
    Exécute une itération complète de l'algorithme de Bellman-Ford.
    
    Une itération = parcourir toutes les arêtes et les relaxer si possible.
    
    Args:
        graphe: Dictionnaire de graphe
        etat: État actuel de l'algorithme
        session_state: État de la session Streamlit
    
    Returns:
        dict: État mis à jour
    """
    if etat["termine"]:
        return etat
    
    # Si on a déjà fait |V|-1 itérations, vérifier les cycles négatifs
    if etat["iteration_courante"] >= etat["nb_iterations_max"]:
        # Vérification des cycles négatifs
        for u, v, poids in etat["aretes"]:
            if (etat["distances"][u] != float('inf') and 
                etat["distances"][u] + poids < etat["distances"][v]):
                etat["cycle_negatif"] = True
                break
        
        etat["termine"] = True
        
        # Enregistrer l'étape finale
        info_etape = {
            "etape": session_state.compteur_etapes + 1,
            "iteration": etat["iteration_courante"],
            "cycle_negatif": etat["cycle_negatif"],
            "distances": {k: (f"{v:.0f}" if v != float('inf') else "∞") 
                         for k, v in etat["distances"].items()},
            "type": "verification_cycle"
        }
        session_state.historique.append(info_etape)
        return etat
    
    # Effectuer une itération de relaxation
    modifie = False
    aretes_relaxees_cette_iteration = []
    
    for u, v, poids in etat["aretes"]:
        if (etat["distances"][u] != float('inf') and 
            etat["distances"][u] + poids < etat["distances"][v]):
            # Relaxation
            ancienne_distance = etat["distances"][v]
            etat["distances"][v] = etat["distances"][u] + poids
            etat["predecesseurs"][v] = u
            modifie = True
            aretes_relaxees_cette_iteration.append((u, v, ancienne_distance, etat["distances"][v]))
    
    etat["aretes_relaxees"] = aretes_relaxees_cette_iteration
    etat["iteration_courante"] += 1
    
    # Enregistrer l'étape
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "iteration": etat["iteration_courante"],
        "aretes_relaxees": aretes_relaxees_cette_iteration,
        "distances": {k: (f"{v:.0f}" if v != float('inf') else "∞") 
                     for k, v in etat["distances"].items()},
        "predecesseurs": dict(etat["predecesseurs"]),
        "type": "iteration"
    }
    session_state.historique.append(info_etape)
    
    # Si aucune modification et qu'on n'a pas atteint le max d'itérations,
    # on peut terminer plus tôt
    if not modifie:
        etat["termine"] = True
    
    return etat


def dessiner_graphe_bellman_ford(graphe, distances, predecesseurs, depart, aretes_relaxees=None, aretes_cycle_negatif=None):
    """
    Dessine le graphe orienté pour l'algorithme de Bellman-Ford.
    
    Args:
        graphe: Dictionnaire de graphe
        distances: Dictionnaire des distances depuis le départ
        predecesseurs: Dictionnaire des prédécesseurs
        depart: Sommet de départ
        aretes_relaxees: Liste des arêtes relaxées à l'itération courante
        aretes_cycle_negatif: Liste des arêtes faisant partie du cycle négatif (à afficher en violet)
    
    Returns:
        matplotlib.figure.Figure
    """
    # Créer un graphe orienté
    G = nx.DiGraph()
    
    # Ajouter tous les sommets d'abord (même ceux sans arêtes sortantes)
    for sommet in graphe.keys():
        G.add_node(sommet)
    
    # Puis ajouter les arêtes
    for u in graphe:
        for v, poids in graphe[u].items():
            G.add_edge(u, v, weight=poids)

    pos = nx.spring_layout(G, seed=42, k=1.5)
    fig, ax = plt.subplots(figsize=(6, 5))

    # Séparer les arêtes positives et négatives
    aretes_positives = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] >= 0]
    aretes_negatives = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] < 0]
    
    # Dessiner les arêtes positives normales
    if aretes_positives:
        nx.draw_networkx_edges(
            G, pos, ax=ax, 
            edgelist=aretes_positives,
            width=1.5, 
            alpha=0.4,
            edge_color='gray',
            arrows=True,
            arrowsize=15,
            arrowstyle='->'
        )
    
    # Dessiner les arêtes négatives en orange
    if aretes_negatives:
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=aretes_negatives,
            width=2,
            alpha=0.6,
            edge_color='#FF9500',
            arrows=True,
            arrowsize=15,
            arrowstyle='->',
            style='dashed'
        )
    
    # Dessiner les arêtes de l'arbre des plus courts chemins en vert
    aretes_chemin = []
    for v, u in predecesseurs.items():
        if u is not None:
            aretes_chemin.append((u, v))
    
    if aretes_chemin:
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=aretes_chemin,
            edge_color='#13C266',
            width=3,
            alpha=1.0,
            arrows=True,
            arrowsize=20,
            arrowstyle='->'
        )
    
    # Dessiner le cycle négatif en violet (par-dessus tout le reste sauf arêtes relaxées)
    if aretes_cycle_negatif:
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=aretes_cycle_negatif,
            edge_color='#9B59B6',  # Violet
            width=4,
            alpha=1.0,
            arrows=True,
            arrowsize=25,
            arrowstyle='->',
            style='solid'
        )
    
    # Dessiner les arêtes relaxées à cette itération en rouge (par-dessus tout)
    if aretes_relaxees:
        aretes_relaxees_simple = [(u, v) for u, v, _, _ in aretes_relaxees]
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=aretes_relaxees_simple,
            edge_color='#B0152A',
            width=4,
            alpha=1.0,
            arrows=True,
            arrowsize=25,
            arrowstyle='->'
        )
    
    # Couleurs des nœuds
    couleurs_noeuds = []
    for noeud in G.nodes():
        if noeud == depart:
            couleurs_noeuds.append("#007AFF")  # Bleu - départ
        elif distances[noeud] != float('inf'):
            couleurs_noeuds.append("#13C266")  # Vert - atteignable
        else:
            couleurs_noeuds.append("white")    # Blanc - non atteignable
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=couleurs_noeuds,
        node_size=500,
        edgecolors="black",
        linewidths=2
    )
    
    # Labels des nœuds
    nx.draw_networkx_labels(G, pos, ax=ax, font_weight="bold", font_size=8)
    
    # Poids des arêtes (afficher avec couleur différente pour les négatifs)
    etiquettes_aretes = nx.get_edge_attributes(G, "weight")
    
    # Formater les labels (arrondir)
    etiquettes_formatees = {k: f"{v:.0f}" for k, v in etiquettes_aretes.items()}
    
    nx.draw_networkx_edge_labels(
        G, pos, ax=ax,
        edge_labels=etiquettes_formatees,
        font_size=6,
        label_pos=0.3
    )

    ax.axis("off")
    fig.tight_layout()
    return fig


def bellman_ford(graphe, depart):
    """
    Algorithme de Bellman-Ford complet (version non pas-à-pas).
    Fonctionne avec des poids négatifs et détecte les cycles négatifs.
    
    Args:
        graphe: Dictionnaire de graphe
        depart: Sommet de départ
    
    Returns:
        tuple: (distances, predecesseurs, cycle_negatif, etapes)
    """
    sommets = list(graphe.keys())
    distances = {sommet: float('inf') for sommet in sommets}
    distances[depart] = 0
    predecesseurs = {sommet: None for sommet in sommets}
    etapes = []
    
    # Extraire toutes les arêtes
    aretes = []
    for u in graphe:
        for v, poids in graphe[u].items():
            aretes.append((u, v, poids))
    
    etapes.append({
        "iteration": 0,
        "distances": distances.copy(),
        "raison": "Initialisation"
    })
    
    # Relaxation |V| - 1 fois
    for i in range(len(sommets) - 1):
        modifie = False
        for u, v, poids in aretes:
            if distances[u] != float('inf') and distances[u] + poids < distances[v]:
                distances[v] = distances[u] + poids
                predecesseurs[v] = u
                modifie = True
        
        etapes.append({
            "iteration": i + 1,
            "distances": distances.copy(),
            "raison": f"Itération {i + 1}"
        })
        
        if not modifie:
            break
    
    # Détection de cycle négatif
    cycle_negatif = False
    for u, v, poids in aretes:
        if distances[u] != float('inf') and distances[u] + poids < distances[v]:
            cycle_negatif = True
            break
    
    return distances, predecesseurs, cycle_negatif, etapes


def floyd_warshall(graphe):
    """
    Algorithme de Floyd-Warshall pour trouver tous les plus courts chemins.
    """
    sommets = list(graphe.keys())
    n = len(sommets)
    
    # Initialisation
    distances = {u: {v: float('inf') for v in sommets} for u in sommets}
    predecesseurs = {u: {v: None for v in sommets} for u in sommets}
    
    # Distance de chaque sommet à lui-même = 0
    for u in sommets:
        distances[u][u] = 0
    
    # Distances directes
    for u in graphe:
        for v, poids in graphe[u].items():
            distances[u][v] = poids
            predecesseurs[u][v] = u  # Le prédécesseur de v est u pour l'arête directe
    
    etapes = []
    etapes.append({
        "k": None,
        "distances": {u: v.copy() for u, v in distances.items()},
        "raison": "Initialisation"
    })
    
    # Algorithme principal
    for k in sommets:
        for i in sommets:
            for j in sommets:
                if distances[i][k] + distances[k][j] < distances[i][j]:
                    distances[i][j] = distances[i][k] + distances[k][j]
                    predecesseurs[i][j] = predecesseurs[i][k] 
        
        etapes.append({
            "k": k,
            "distances": {u: v.copy() for u, v in distances.items()},
            "raison": f"Via sommet {k}"
        })
    
    return distances, predecesseurs, etapes