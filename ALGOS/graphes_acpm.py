import networkx as nx
import matplotlib.pyplot as plt
import heapq
class EnsemblesDisjoints:
    """
    Permet de détecter efficacement les cycles lors de la construction de l'arbre.
    """
    def __init__(self, sommets):
        self.parent = {sommet: sommet for sommet in sommets}
        self.rang = {sommet: 0 for sommet in sommets}
    
    def find(self, sommet):
        """Trouve la racine de l'ensemble contenant le sommet (avec compression de chemin).
        """
        if self.parent[sommet] != sommet:
            self.parent[sommet] = self.find(self.parent[sommet])
        return self.parent[sommet]
    
    def union(self, sommet1, sommet2):
        """
        Fusionne les ensembles contenant sommet1 et sommet2.
        Retourne True si la fusion a eu lieu, False si déjà dans le même ensemble.
        """
        racine1 = self.find(sommet1)
        racine2 = self.find(sommet2)
        
        if racine1 == racine2:
            return False
        
        # Union par rang pour optimiser
        if self.rang[racine1] < self.rang[racine2]:
            self.parent[racine1] = racine2
        elif self.rang[racine1] > self.rang[racine2]:
            self.parent[racine2] = racine1
        else:
            self.parent[racine2] = racine1
            self.rang[racine1] += 1
        
        return True


def kruskal(graphe):
    """
    Algorithme de Kruskal pour trouver l'arbre couvrant de poids minimum.
    
    Principe:
    1. Trier toutes les arêtes par poids croissant
    2. Pour chaque arête, l'ajouter si elle ne crée pas de cycle
    3. S'arrêter quand on a n-1 arêtes (n = nombre de sommets)
    """
    # Extraire toutes les arêtes
    aretes = []
    aretes_vues = set()
    
    for u in graphe:
        for v, poids in graphe[u].items():
            # Éviter les doublons (u,v) et (v,u)
            arete = tuple(sorted([u, v]))
            if arete not in aretes_vues:
                aretes_vues.add(arete)
                aretes.append((poids, u, v))
    
    # Trier les arêtes par poids croissant
    aretes.sort()
    
    # Initialiser Union-Find
    sommets = list(graphe.keys())
    uf = EnsemblesDisjoints(sommets)
    
    # Construction de l'arbre
    arbre_couvrant = []
    cout_total = 0
    etapes = []
    
    for poids, u, v in aretes:
        # Vérifier si ajouter cette arête crée un cycle
        if uf.union(u, v):
            arbre_couvrant.append((u, v, poids))
            cout_total += poids
            
            etapes.append({
                "arete": (u, v),
                "poids": poids,
                "accepte": True,
                "raison": f"Arête ajoutée (pas de cycle)",
                "arbre_actuel": list(arbre_couvrant)
            })
            
            # Si on a n-1 arêtes, l'arbre est complet
            if len(arbre_couvrant) == len(sommets) - 1:
                break
        else:
            etapes.append({
                "arete": (u, v),
                "poids": poids,
                "accepte": False,
                "raison": f"Arête rejetée (créerait un cycle)",
                "arbre_actuel": list(arbre_couvrant)
            })
    
    return arbre_couvrant, cout_total, etapes


def prim(graphe, depart=None):
    """
    Algorithme de Prim pour trouver l'arbre couvrant de poids minimum.
    
    Principe:
    1. Partir d'un sommet initial
    2. À chaque étape, ajouter l'arête de poids minimum qui connecte
       un sommet de l'arbre à un sommet hors de l'arbre
    3. Continuer jusqu'à avoir tous les sommets
    """
    if not graphe:
        return [], 0, []
    
    # Choisir le sommet de départ
    if depart is None:
        depart = sorted(list(graphe.keys()))[0]
    
    # Initialisation
    visites = set([depart])
    arbre_couvrant = []
    cout_total = 0
    etapes = []
    
    # File de priorité: (poids, sommet_dans_arbre, sommet_hors_arbre)
    file_priorite = []
    
    # Ajouter toutes les arêtes partant du sommet de départ
    for voisin, poids in graphe[depart].items():
        heapq.heappush(file_priorite, (poids, depart, voisin))
    
    etapes.append({
        "sommet_ajoute": depart,
        "arete": None,
        "poids": 0,
        "visites": visites.copy(),
        "raison": "Sommet de départ",
        "arbre_actuel": []
    })
    
    # Construction de l'arbre
    while file_priorite and len(visites) < len(graphe):
        poids, u, v = heapq.heappop(file_priorite)
        
        # Si v est déjà visité, ignorer cette arête
        if v in visites:
            continue
        
        # Ajouter l'arête à l'arbre
        arbre_couvrant.append((u, v, poids))
        cout_total += poids
        visites.add(v)
        
        etapes.append({
            "sommet_ajoute": v,
            "arete": (u, v),
            "poids": poids,
            "visites": visites.copy(),
            "raison": f"Arête de poids minimum: {u} → {v} (poids: {poids})",
            "arbre_actuel": list(arbre_couvrant)
        })
        
        # Ajouter toutes les arêtes partant de v vers des sommets non visités
        for voisin, poids_voisin in graphe[v].items():
            if voisin not in visites:
                heapq.heappush(file_priorite, (poids_voisin, v, voisin))
    
    return arbre_couvrant, cout_total, etapes


def init_prim(graphe, depart):
    """Initialise l'état du parcours Prim.
    """
    return {
        "visites": [depart],  # Liste pour conserver l'ordre chronologique
        "arbre": [],
        "cout_total": 0,
        "file_priorite": [(poids, depart, voisin) for voisin, poids in graphe[depart].items()],
        "sommet_courant": depart,
        "termine": False
    }


def etape_prim(graphe, etat, session_state):
    """Exécute une étape de l'algorithme de Prim.
    """
    if not etat["file_priorite"] or len(etat["visites"]) >= len(graphe):
        etat["termine"] = True
        return etat
    
    # Extraire l'arête de poids minimum
    heapq.heapify(etat["file_priorite"])
    
    # Trouver la première arête valide (vers un sommet non visité)
    while etat["file_priorite"]:
        poids, u, v = heapq.heappop(etat["file_priorite"])
        
        if v not in etat["visites"]:
            # Ajouter l'arête et le sommet
            etat["arbre"].append((u, v, poids))
            etat["cout_total"] += poids
            etat["visites"].append(v)  # Ajouter à la liste dans l'ordre chronologique
            etat["sommet_courant"] = v
            
            # Ajouter les nouvelles arêtes
            for voisin, poids_voisin in graphe[v].items():
                if voisin not in etat["visites"]:
                    heapq.heappush(etat["file_priorite"], (poids_voisin, v, voisin))
            
            # Enregistrer l'étape (ordre chronologique conservé)
            info_etape = {
                "etape": session_state.compteur_etapes + 1,
                "sommet": v,
                "arete": (u, v),
                "poids": poids,
                "cout_total": etat["cout_total"],
                "visites": list(etat["visites"]),  # Ordre chronologique conservé
                "arbre": list(etat["arbre"])
            }
            session_state.historique.append(info_etape)
            break
    
    return etat


def init_kruskal(graphe):
    """Initialise l'état de l'algorithme de Kruskal.
    """
    # Extraire et trier toutes les arêtes
    aretes = []
    aretes_vues = set()
    
    for u in graphe:
        for v, poids in graphe[u].items():
            arete = tuple(sorted([u, v]))
            if arete not in aretes_vues:
                aretes_vues.add(arete)
                aretes.append((poids, u, v))
    
    aretes.sort()
    
    return {
        "aretes_triees": aretes,
        "arbre": [],
        "cout_total": 0,
        "uf": EnsemblesDisjoints(list(graphe.keys())),
        "index_arete": 0,
        "arete_courante": None,
        "termine": False
    }


def etape_kruskal(graphe, etat, session_state):
    """Exécute une étape de l'algorithme de Kruskal.
    """
    if etat["index_arete"] >= len(etat["aretes_triees"]) or len(etat["arbre"]) >= len(graphe) - 1:
        etat["termine"] = True
        return etat
    
    poids, u, v = etat["aretes_triees"][etat["index_arete"]]
    etat["arete_courante"] = (u, v)
    
    accepte = etat["uf"].union(u, v)
    
    if accepte:
        etat["arbre"].append((u, v, poids))
        etat["cout_total"] += poids
    
    # Enregistrer l'étape
    info_etape = {
        "etape": session_state.compteur_etapes + 1,
        "arete": (u, v),
        "poids": poids,
        "accepte": accepte,
        "cout_total": etat["cout_total"],
        "arbre": list(etat["arbre"])
    }
    session_state.historique.append(info_etape)
    
    etat["index_arete"] += 1
    
    return etat


def dessiner_graphe_acm(graphe, arbre_couvrant=None, sommet_courant=None):
    """
    Dessine le graphe avec l'arbre couvrant mis en évidence.
    """
    G = nx.Graph()
    for u in graphe:
        for v, poids in graphe[u].items():
            G.add_edge(u, v, weight=poids)

    pos = nx.spring_layout(G, weight="weight", seed=42, k=1.2)

    fig, ax = plt.subplots(figsize=(6, 5))

    # Dessiner toutes les arêtes avec le même style que dessiner_graphe
    nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, alpha=0.4)
    
    # Redessiner l'arbre couvrant en vert par-dessus
    if arbre_couvrant:
        aretes_acm = [(u, v) for u, v, _ in arbre_couvrant]
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=aretes_acm,
            edge_color='#13C266',
            width=3,
            alpha=1.0
        )
    
    # Couleurs des nœuds
    if arbre_couvrant:
        sommets_arbre = set()
        for u, v, _ in arbre_couvrant:
            sommets_arbre.add(u)
            sommets_arbre.add(v)
        
        couleurs_noeuds = []
        for noeud in G.nodes():
            if noeud == sommet_courant:
                couleurs_noeuds.append("#B0152A")  # Rouge - sommet courant
            elif noeud in sommets_arbre:
                couleurs_noeuds.append("#13C266")  # Vert - dans l'arbre
            else:
                couleurs_noeuds.append("white")    # Blanc - pas encore
    else:
        couleurs_noeuds = ["white"] * len(G.nodes())
    
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
    
    # Dessiner tous les poids des arêtes (comme dans dessiner_graphe)
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
