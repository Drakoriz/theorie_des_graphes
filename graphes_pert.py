import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta


class TachePERT:
    """Représente une tâche dans le graphe PERT."""
    
    def __init__(self, id_tache, nom, duree, dependances=None):
        """
        Initialise une tâche PERT.
        
        Args:
            id_tache: Identifiant unique de la tâche (ex: "A", "B", "C")
            nom: Nom descriptif de la tâche
            duree: Durée de la tâche (en jours)
            dependances: Liste des IDs des tâches dont celle-ci dépend
        """
        self.id = id_tache
        self.nom = nom
        self.duree = duree
        self.dependances = dependances if dependances else []
        
        # Calculs PERT
        self.date_debut_tot = 0  # Date au plus tôt de début
        self.date_fin_tot = 0    # Date au plus tôt de fin
        self.date_debut_tard = 0 # Date au plus tard de début
        self.date_fin_tard = 0   # Date au plus tard de fin
        self.marge_totale = 0    # Marge totale
        self.marge_libre = 0     # Marge libre
        self.est_critique = False # Sur le chemin critique ?
    
    def __repr__(self):
        return f"Tâche({self.id}: {self.nom}, durée={self.duree}j)"


def creer_projet_construction_maison():
    """
    Crée un projet : Construction d'une maison individuelle.
    
    Projet complet avec 12 tâches représentant toutes les phases
    de construction d'une maison, des fondations à la livraison.
    """
    taches = [
        TachePERT("A", "Étude de faisabilité et choix du terrain", 7, []),
        TachePERT("B", "Obtention du permis de construire", 10, ["A"]),
        TachePERT("C", "Plans architecte et étude structure", 8, ["A"]),
        TachePERT("D", "Terrassement et fondations", 12, ["B", "C"]),
        TachePERT("E", "Élévation des murs et charpente", 15, ["D"]),
        TachePERT("F", "Pose de la toiture et isolation", 10, ["E"]),
        TachePERT("G", "Installation électricité et plomberie", 14, ["E"]),
        TachePERT("H", "Menuiseries extérieures (fenêtres, portes)", 6, ["F"]),
        TachePERT("I", "Revêtements intérieurs (plâtre, peinture)", 12, ["G", "H"]),
        TachePERT("J", "Pose des sols et carrelage", 8, ["I"]),
        TachePERT("K", "Installation cuisine et salle de bains", 7, ["J"]),
        TachePERT("L", "Aménagement extérieur et réception chantier", 5, ["K"])
    ]
    return taches


def calculer_dates_tot(taches):
    """
    Calcule les dates au plus tôt (forward pass).
    
    Args:
        taches: Liste des tâches PERT
    
    Returns:
        dict: Dictionnaire {id_tache: tache} pour accès rapide
    """
    # Créer un dictionnaire pour accès rapide
    taches_dict = {t.id: t for t in taches}
    
    # Initialiser toutes les dates à 0
    for tache in taches:
        tache.date_debut_tot = 0
        tache.date_fin_tot = 0
    
    # Parcours topologique (forward pass)
    # On traite les tâches dans l'ordre de leurs dépendances
    taches_traitees = set()
    
    while len(taches_traitees) < len(taches):
        for tache in taches:
            if tache.id in taches_traitees:
                continue
            
            # Vérifier que toutes les dépendances sont traitées
            if all(dep in taches_traitees for dep in tache.dependances):
                # Si pas de dépendances, commence à 0
                if not tache.dependances:
                    tache.date_debut_tot = 0
                else:
                    # Sinon, commence après la fin au plus tôt de toutes les dépendances
                    tache.date_debut_tot = max(
                        taches_dict[dep].date_fin_tot 
                        for dep in tache.dependances
                    )
                
                tache.date_fin_tot = tache.date_debut_tot + tache.duree
                taches_traitees.add(tache.id)
    
    return taches_dict


def calculer_dates_tard(taches, taches_dict):
    """
    Calcule les dates au plus tard (backward pass).
    
    Args:
        taches: Liste des tâches PERT
        taches_dict: Dictionnaire {id_tache: tache}
    """
    if not taches:
        return
    
    # Trouver la date de fin du projet (max des dates de fin au plus tôt)
    date_fin_projet = max(t.date_fin_tot for t in taches)
    
    # Initialiser les tâches finales
    for tache in taches:
        # Identifier les tâches qui ne sont pas dépendances d'autres tâches
        est_finale = True
        for autre_tache in taches:
            if tache.id in autre_tache.dependances:
                est_finale = False
                break
        
        if est_finale:
            tache.date_fin_tard = date_fin_projet
            tache.date_debut_tard = tache.date_fin_tard - tache.duree
    
    # Parcours inverse (backward pass)
    taches_traitees = set(t.id for t in taches if t.date_fin_tard > 0)
    
    while len(taches_traitees) < len(taches):
        for tache in taches:
            if tache.id in taches_traitees:
                continue
            
            # Trouver toutes les tâches qui dépendent de celle-ci
            successeurs = [t for t in taches if tache.id in t.dependances]
            
            # Vérifier que tous les successeurs sont traités
            if all(s.id in taches_traitees for s in successeurs):
                if successeurs:
                    # La date de fin au plus tard est le min des dates de début au plus tard des successeurs
                    tache.date_fin_tard = min(s.date_debut_tard for s in successeurs)
                    tache.date_debut_tard = tache.date_fin_tard - tache.duree
                else:
                    # Si pas de successeurs (ne devrait pas arriver après init)
                    tache.date_fin_tard = date_fin_projet
                    tache.date_debut_tard = tache.date_fin_tard - tache.duree
                
                taches_traitees.add(tache.id)


def calculer_marges(taches, taches_dict):
    """
    Calcule les marges totales et libres.
    
    Args:
        taches: Liste des tâches PERT
        taches_dict: Dictionnaire {id_tache: tache}
    """
    for tache in taches:
        # Marge totale = date au plus tard de début - date au plus tôt de début
        tache.marge_totale = tache.date_debut_tard - tache.date_debut_tot
        
        # Marge libre = min(date début au plus tôt des successeurs) - date fin au plus tôt
        successeurs = [t for t in taches if tache.id in t.dependances]
        
        if successeurs:
            tache.marge_libre = min(s.date_debut_tot for s in successeurs) - tache.date_fin_tot
        else:
            # Pour les tâches finales, marge libre = marge totale
            tache.marge_libre = tache.marge_totale
        
        # Une tâche est critique si sa marge totale est nulle (ou proche de 0)
        tache.est_critique = abs(tache.marge_totale) < 0.001


def identifier_chemin_critique(taches):
    """
    Identifie le chemin critique (ensemble des tâches critiques).
    
    Args:
        taches: Liste des tâches PERT
    
    Returns:
        list: Liste des IDs des tâches sur le chemin critique
    """
    return [t.id for t in taches if t.est_critique]


def calculer_pert(taches):
    """
    Calcule toutes les valeurs PERT pour un ensemble de tâches.
    
    Args:
        taches: Liste des tâches PERT
    
    Returns:
        tuple: (taches_dict, chemin_critique, duree_projet)
    """
    if not taches:
        return {}, [], 0
    
    # Calculer les dates au plus tôt
    taches_dict = calculer_dates_tot(taches)
    
    # Calculer les dates au plus tard
    calculer_dates_tard(taches, taches_dict)
    
    # Calculer les marges
    calculer_marges(taches, taches_dict)
    
    # Identifier le chemin critique
    chemin_critique = identifier_chemin_critique(taches)
    
    # Durée totale du projet
    duree_projet = max(t.date_fin_tot for t in taches) if taches else 0
    
    return taches_dict, chemin_critique, duree_projet


def dessiner_diagramme_pert(taches, chemin_critique):
    """
    Dessine un diagramme PERT avec NetworkX.
    
    Args:
        taches: Liste des tâches PERT
        chemin_critique: Liste des IDs des tâches critiques
    
    Returns:
        matplotlib.figure.Figure
    """
    if not taches:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Aucune tâche à afficher', 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    G = nx.DiGraph()
    
    # Ajouter les nœuds
    for tache in taches:
        G.add_node(tache.id, tache=tache)
    
    # Ajouter les arêtes (dépendances)
    for tache in taches:
        for dep in tache.dependances:
            G.add_edge(dep, tache.id)
    
    # Utiliser un layout hiérarchique
    try:
        pos = nx.planar_layout(G)
    except:
        try:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        except:
            pos = nx.kamada_kawai_layout(G)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Dessiner les arêtes normales
    aretes_normales = [(u, v) for u, v in G.edges() 
                       if u not in chemin_critique or v not in chemin_critique]
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aretes_normales, 
                          width=1.5, alpha=0.4, arrows=True, 
                          arrowsize=20, arrowstyle='->', edge_color='gray')
    
    # Dessiner les arêtes du chemin critique en rouge
    aretes_critiques = [(u, v) for u, v in G.edges() 
                       if u in chemin_critique and v in chemin_critique]
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aretes_critiques,
                          width=3, alpha=1.0, arrows=True,
                          arrowsize=25, arrowstyle='->', edge_color='#B0152A')
    
    # Couleurs des nœuds
    couleurs_noeuds = []
    for noeud in G.nodes():
        if noeud in chemin_critique:
            couleurs_noeuds.append("#B0152A")  # Rouge pour critique
        else:
            couleurs_noeuds.append("#13C266")  # Vert pour non-critique
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(G, pos, ax=ax,
                          node_color=couleurs_noeuds,
                          node_size=2500,
                          edgecolors="black",
                          linewidths=2)
    
    # Créer des labels complexes avec les informations PERT
    labels = {}
    for noeud in G.nodes():
        tache = G.nodes[noeud]['tache']
        # Format: ID
        #         Nom
        #         Durée
        #         Dates
        labels[noeud] = f"{tache.id}\n{tache.nom[:15]}...\n{tache.duree}j"
    
    nx.draw_networkx_labels(G, pos, ax=ax, labels=labels,
                           font_size=7, font_weight="bold", font_color="white")
    
    ax.axis("off")
    ax.set_title("Diagramme PERT", fontsize=16, fontweight='bold', pad=20)
    
    # Ajouter une légende
    legende_elements = [
        mpatches.Patch(color='#B0152A', label='Tâche critique'),
        mpatches.Patch(color='#13C266', label='Tâche non-critique')
    ]
    ax.legend(handles=legende_elements, loc='upper right', fontsize=10)
    
    fig.tight_layout()
    return fig


def dessiner_diagramme_gantt(taches, chemin_critique, date_debut_projet=None):
    """
    Dessine un diagramme de Gantt.
    
    Args:
        taches: Liste des tâches PERT
        chemin_critique: Liste des IDs des tâches critiques
        date_debut_projet: Date de début du projet (datetime ou None)
    
    Returns:
        matplotlib.figure.Figure
    """
    if not taches:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Aucune tâche à afficher', 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    if date_debut_projet is None:
        date_debut_projet = datetime.now()
    
    # Trier les tâches par date de début au plus tôt
    taches_triees = sorted(taches, key=lambda t: t.date_debut_tot)
    
    fig, ax = plt.subplots(figsize=(14, max(8, len(taches) * 0.5)))
    
    # Couleurs
    couleur_critique = '#B0152A'
    couleur_normale = '#13C266'
    couleur_marge = '#E0E0E0'
    
    y_pos = 0
    y_labels = []
    y_ticks = []
    
    for tache in taches_triees:
        y_labels.append(f"{tache.id}: {tache.nom}")
        y_ticks.append(y_pos)
        
        # Barre pour la durée de la tâche
        couleur = couleur_critique if tache.est_critique else couleur_normale
        ax.barh(y_pos, tache.duree, left=tache.date_debut_tot, 
               height=0.6, color=couleur, edgecolor='black', linewidth=1.5)
        
        # Si marge totale > 0, dessiner la marge en gris clair
        if tache.marge_totale > 0:
            ax.barh(y_pos, tache.marge_totale, left=tache.date_fin_tot,
                   height=0.6, color=couleur_marge, edgecolor='black', 
                   linewidth=1, linestyle='--', alpha=0.5)
        
        # Ajouter la durée sur la barre
        ax.text(tache.date_debut_tot + tache.duree / 2, y_pos,
               f'{tache.duree}j', ha='center', va='center',
               fontweight='bold', fontsize=8, color='white')
        
        y_pos += 1
    
    # Configuration des axes
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.set_xlabel('Temps (jours)', fontsize=12, fontweight='bold')
    ax.set_title('Diagramme de Gantt', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Inverser l'axe Y pour avoir la première tâche en haut
    ax.invert_yaxis()
    
    # Ajuster les limites
    if taches:
        duree_max = max(t.date_fin_tard for t in taches)
        ax.set_xlim(0, duree_max * 1.05)
    else:
        ax.set_xlim(0, 10)
    
    # Ajouter une légende
    legende_elements = [
        mpatches.Patch(color=couleur_critique, label='Tâche critique'),
        mpatches.Patch(color=couleur_normale, label='Tâche non-critique'),
        mpatches.Patch(color=couleur_marge, label='Marge disponible', alpha=0.5)
    ]
    ax.legend(handles=legende_elements, loc='lower right', fontsize=10)
    
    fig.tight_layout()
    return fig


def generer_tableau_pert(taches):
    """
    Génère un tableau récapitulatif des calculs PERT.
    
    Args:
        taches: Liste des tâches PERT
    
    Returns:
        list: Liste de dictionnaires pour créer un DataFrame
    """
    tableau = []
    for tache in sorted(taches, key=lambda t: t.id):
        tableau.append({
            "ID": tache.id,
            "Tâche": tache.nom,
            "Durée (j)": tache.duree,
            "Dépendances": ", ".join(tache.dependances) if tache.dependances else "-",
            "Début tôt": int(tache.date_debut_tot),
            "Fin tôt": int(tache.date_fin_tot),
            "Début tard": int(tache.date_debut_tard),
            "Fin tard": int(tache.date_fin_tard),
            "Marge totale": int(tache.marge_totale),
            "Marge libre": int(tache.marge_libre),
            "Critique": "" if tache.est_critique else ""
        })
    return tableau


def valider_taches(taches):
    """
    Valide qu'un ensemble de tâches est cohérent.
    
    Args:
        taches: Liste des tâches PERT
    
    Returns:
        tuple: (bool, str) - (valide, message d'erreur)
    """
    if not taches:
        return False, "Aucune tâche définie"
    
    # Vérifier les IDs uniques
    ids = [t.id for t in taches]
    if len(ids) != len(set(ids)):
        return False, "Les IDs des tâches doivent être uniques"
    
    # Vérifier que toutes les dépendances existent
    ids_set = set(ids)
    for tache in taches:
        for dep in tache.dependances:
            if dep not in ids_set:
                return False, f"La tâche {tache.id} dépend de {dep} qui n'existe pas"
    
    # Vérifier qu'il n'y a pas de cycles
    try:
        G = nx.DiGraph()
        for tache in taches:
            G.add_node(tache.id)
        for tache in taches:
            for dep in tache.dependances:
                G.add_edge(dep, tache.id)
        
        if not nx.is_directed_acyclic_graph(G):
            return False, "Le graphe contient des cycles (dépendances circulaires)"
    except Exception as e:
        return False, f"Erreur lors de la validation : {str(e)}"
    
    # Vérifier les durées positives
    for tache in taches:
        if tache.duree <= 0:
            return False, f"La tâche {tache.id} a une durée invalide ({tache.duree})"
    
    return True, "Tâches valides"