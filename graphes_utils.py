import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def charger_graphe(chemin_csv):
    """
    Charge un graphe depuis un fichier CSV.
    """
    df = pd.read_csv(chemin_csv, sep=";")
    graphe = {}
    for _, ligne in df.iterrows():
        u = ligne["ville_a"]
        v = ligne["ville_b"]
        poids = float(ligne["distance"])
        graphe.setdefault(u, {})[v] = poids
        graphe.setdefault(v, {})[u] = poids
    return graphe


def dessiner_graphe(graphe, visites, courant=None, en_file=None):
    """
    Dessine le graphe avec coloration des nœuds selon leur état.
    Affiche également le numéro d'ordre de visite au-dessus des nœuds visités.
    """
    G = nx.Graph()
    for u in graphe:
        for v, poids in graphe[u].items():
            G.add_edge(u, v, weight=poids)

    pos = nx.spring_layout(G, weight="weight", seed=42, k=1.2)

    if en_file is None:
        en_file = set()

    # Convertir visites en liste si c'est un ensemble
    if isinstance(visites, set):
        visites_list = list(visites)
    else:
        visites_list = visites if isinstance(visites, list) else []

    # Définir les couleurs des nœuds selon leur état
    couleurs_noeuds = []
    for noeud in G.nodes():
        if noeud == courant:
            couleurs_noeuds.append("#B0152A")  # Rouge - nœud courant
        elif noeud in en_file:
            couleurs_noeuds.append("#FF9500")  # Orange - en file/pile
        elif noeud in visites_list:
            couleurs_noeuds.append("#13C266")  # Vert - visité
        else:
            couleurs_noeuds.append("white")    # Blanc - non visité

    fig, ax = plt.subplots(figsize=(6, 5))

    # Dessiner les arêtes
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.4)
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=couleurs_noeuds,
        node_size=500,
        edgecolors="black",
        linewidths=2
    )
    
    # Dessiner les labels des nœuds
    nx.draw_networkx_labels(G, pos, ax=ax, font_weight="bold", font_size=8)

    # Dessiner les numéros d'ordre de visite au-dessus des nœuds visités
    if visites_list and len(visites_list) > 0:
        # Créer un dictionnaire des numéros d'ordre pour les nœuds visités
        numeros_ordre = {}
        for i, noeud in enumerate(visites_list, start=1):
            if noeud in G.nodes():
                numeros_ordre[noeud] = str(i)
        
        # Dessiner les numéros d'ordre au-dessus des nœuds
        for noeud, numero in numeros_ordre.items():
            if noeud in pos:
                x, y = pos[noeud]
                # Position au-dessus du nœud
                y_offset = 0.15
                ax.text(x, y + y_offset, numero, 
                       ha='center', va='center',
                       fontsize=10, fontweight='bold',
                       color='#1a1a1a',
                       bbox=dict(boxstyle='circle,pad=0.3', 
                               facecolor='white', 
                               edgecolor='#1a1a1a',
                               linewidth=1.5),
                       zorder=10)

    # Dessiner les poids des arêtes
    etiquettes_aretes = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G, pos, ax=ax, edge_labels=etiquettes_aretes,
        font_size=6, label_pos=0.3
    )

    ax.axis("off")
    fig.tight_layout()
    return fig


def transformer_graphe_oriente_simple_from_df(df):
    """
    Transforme un DataFrame de graphe en graphe orienté simple.
    Respecte l'ordre exact ville_a → ville_b du CSV original.
    
    Args:
        df: DataFrame avec colonnes ville_a, ville_b, distance
    
    Returns:
        dict: Graphe orienté où chaque arête va de ville_a vers ville_b
    """
    graphe_oriente = {}
    
    # Initialiser tous les sommets
    villes = set(df['ville_a'].unique()) | set(df['ville_b'].unique())
    for ville in villes:
        graphe_oriente[ville] = {}
    
    # Ajouter les arêtes orientées selon l'ordre du CSV
    for _, ligne in df.iterrows():
        u = str(ligne["ville_a"]).strip()
        v = str(ligne["ville_b"]).strip()
        poids = float(ligne["distance"])
        
        # Créer l'arête u -> v (ville_a -> ville_b)
        graphe_oriente[u][v] = poids
    
    return graphe_oriente


def verifier_connexite_orientee(graphe):
    """
    Vérifie si un graphe orienté est fortement connexe.
    
    Args:
        graphe: Dictionnaire du graphe orienté
    
    Returns:
        bool: True si fortement connexe, False sinon
    """
    import networkx as nx
    
    if not graphe:
        return False
    
    G = nx.DiGraph()
    for u in graphe:
        G.add_node(u)
        for v in graphe[u]:
            G.add_edge(u, v)
    
    return nx.is_strongly_connected(G)


def ajouter_cycle_negatif(graphe):
    """
    Ajoute un cycle négatif dans le graphe orienté.
    Trouve un cycle existant et modifie les poids pour créer un cycle négatif.
    
    Args:
        graphe: Dictionnaire du graphe orienté
    
    Returns:
        tuple: (Nouveau graphe avec un cycle négatif, liste des arêtes du cycle) ou (None, None) si impossible
    """
    import random
    import networkx as nx
    
    # Créer un graphe NetworkX pour trouver les cycles
    G = nx.DiGraph()
    for u in graphe:
        for v in graphe[u]:
            G.add_edge(u, v)
    
    try:
        # Trouver tous les cycles simples (limité à 100 pour performance)
        cycles = list(nx.simple_cycles(G))
        
        if not cycles:
            return None, None
        
        # Choisir un cycle aléatoire (préférer les cycles de longueur 3-5)
        cycles_courts = [c for c in cycles if 3 <= len(c) <= 5]
        if cycles_courts:
            cycle = random.choice(cycles_courts)
        else:
            cycle = random.choice(cycles)
        
        # Copier le graphe
        graphe_cycle = {}
        for u in graphe:
            graphe_cycle[u] = dict(graphe[u])
        
        # Calculer le poids total du cycle
        poids_total = 0
        aretes_cycle = []
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            if v in graphe_cycle[u]:
                poids_total += graphe_cycle[u][v]
                aretes_cycle.append((u, v))
        
        # Rendre une arête suffisamment négative pour créer un cycle négatif
        if aretes_cycle:
            u, v = aretes_cycle[0]
            # Rendre négative avec une marge
            graphe_cycle[u][v] = -(poids_total + 50)
        
        return graphe_cycle, aretes_cycle
    
    except:
        return None, None