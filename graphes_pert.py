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
    Crée un projet : 
    
    Projet complet avec 12 tâches représentant toutes les phases
    d'une soirée de lancement (exemple de Graphe PERT Objectif BTS Hachette) '
    """
    taches = [
        TachePERT("A", "Commande", 20, []),
        TachePERT("B", "Recrutement", 30, []),
        TachePERT("C", "Plan de communication", 10, []),
        TachePERT("D", "Installation", 3, ["A"]),
        TachePERT("E", "Entretiens", 3, ["B"]),
        TachePERT("F", "Formation", 3, ["D","E"]),
        TachePERT("G", "Réservations", 30, ["C"]),
        TachePERT("H", "Commandes des affiches", 15, ["G"]),
        TachePERT("I", "Animations", 4, ["F", "H"]),
        TachePERT("J", "Commande des fleurs", 10, ["D"]),
        TachePERT("K", "Décoration", 7, ["F","J"]),
        TachePERT("L", "Cocktail", 1, ["I","K"])
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
    Dessine un diagramme PERT VERTICAL clair et lisible avec meilleure scalabilité.
    
    Format du nœud :
    - Haut gauche : Date au plus tôt
    - Haut droite : Date au plus tard  
    - Bas : Marge totale
    
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
    
    # Créer le graphe avec nœud de début
    G = nx.DiGraph()
    
    # Ajouter un nœud de début fictif
    G.add_node("DEBUT", tache=None)
    
    # Ajouter les tâches
    for tache in taches:
        G.add_node(tache.id, tache=tache)
    
    # Connecter le début aux tâches sans dépendances
    for tache in taches:
        if not tache.dependances:
            G.add_edge("DEBUT", tache.id)
    
    # Ajouter les arêtes (dépendances)
    for tache in taches:
        for dep in tache.dependances:
            G.add_edge(dep, tache.id)
    
    # Calculer les niveaux (maintenant verticaux) - POSITIONNEMENT MANUEL
    niveaux = {"DEBUT": 0}
    for tache in taches:
        if not tache.dependances:
            niveaux[tache.id] = 1
        else:
            niveaux[tache.id] = max(niveaux.get(dep, 0) for dep in tache.dependances) + 1
    
    # Organiser les tâches par niveau
    taches_par_niveau = {}
    for node_id, niveau in niveaux.items():
        if niveau not in taches_par_niveau:
            taches_par_niveau[niveau] = []
        taches_par_niveau[niveau].append(node_id)
    
    # Positionnement manuel pour éviter les chevauchements
    # ORIENTATION VERTICALE : on inverse X et Y
    pos = {}
    espacement_y = 2.5  # Espacement VERTICAL entre niveaux (réduit de moitié)
    espacement_x = 2.0  # Espacement HORIZONTAL entre tâches (réduit)
    
    for niveau, nodes in taches_par_niveau.items():
        nb_nodes = len(nodes)
        y = -niveau * espacement_y  # Négatif pour aller vers le bas
        
        # Centrer horizontalement les nœuds de ce niveau
        largeur_totale = (nb_nodes - 1) * espacement_x
        x_start = -largeur_totale / 2
        
        for i, node_id in enumerate(sorted(nodes)):
            x = x_start + i * espacement_x
            pos[node_id] = (x, y)
    
    # Format VERTICAL : plus haut que large
    max_niveau = max(niveaux.values()) if niveaux else 1
    nb_max_par_niveau = max(len(nodes) for nodes in taches_par_niveau.values())
    
    # Dimensions adaptées pour format vertical (réduites pour correspondre aux espacements)
    largeur = max(8, nb_max_par_niveau * 2.0 + 2)
    hauteur = max(8, max_niveau * 2.5 + 3)
    
    fig, ax = plt.subplots(figsize=(largeur, hauteur))
    
    # Dessiner d'abord toutes les arêtes
    for u, v in G.edges():
        if u == "DEBUT":
            continue
            
        # Déterminer la couleur de l'arête
        if u in chemin_critique and v in chemin_critique:
            couleur = '#E63946'  # Rouge vif pour chemin critique
            largeur_line = 4.0
            alpha = 1.0
        else:
            couleur = '#457B9D'  # Bleu pour non-critique
            largeur_line = 2.5
            alpha = 0.6
        
        # Dessiner l'arête
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', lw=largeur_line, 
                                 color=couleur, alpha=alpha,
                                 shrinkA=30, shrinkB=30))
    
    # Dessiner les nœuds
    for node_id in G.nodes():
        if node_id == "DEBUT":
            # Nœud spécial pour le début (cercle bleu)
            x, y = pos[node_id]
            cercle = mpatches.Circle((x, y), radius=0.35, 
                                    color='#1D3557', ec='black', 
                                    linewidth=3, zorder=10)
            ax.add_patch(cercle)
            ax.text(x, y, "DÉBUT", ha='center', va='center',
                   fontsize=12, fontweight='bold', color='white', zorder=11)
            continue
        
        tache = G.nodes[node_id]['tache']
        x, y = pos[node_id]
        
        # Dimensions du rectangle (augmentées pour meilleure lisibilité)
        largeur_rect = 0.85
        hauteur_rect = 0.65
        
        # Couleur selon si critique
        if node_id in chemin_critique:
            couleur_fond = '#FFE5E5'
            couleur_bordure = '#E63946'
            largeur_bordure = 3.5
        else:
            couleur_fond = '#E8F4F8'
            couleur_bordure = '#457B9D'
            largeur_bordure = 2.5
        
        # Dessiner le rectangle principal
        rect = mpatches.FancyBboxPatch(
            (x - largeur_rect/2, y - hauteur_rect/2),
            largeur_rect, hauteur_rect,
            boxstyle="round,pad=0.02",
            facecolor=couleur_fond,
            edgecolor=couleur_bordure,
            linewidth=largeur_bordure,
            zorder=10
        )
        ax.add_patch(rect)
        
        # Dessiner les lignes de séparation (croix légère)
        # Ligne verticale
        ax.plot([x, x], [y - hauteur_rect/2, y + hauteur_rect/2], 
               color=couleur_bordure, linewidth=2, alpha=0.5, zorder=11)
        # Ligne horizontale
        ax.plot([x - largeur_rect/2, x + largeur_rect/2], [y, y], 
               color=couleur_bordure, linewidth=2, alpha=0.5, zorder=11)
        
        # Textes dans le rectangle (taille de police augmentée)
        # Haut gauche : Date au plus tôt (noir)
        ax.text(x - largeur_rect/4, y + hauteur_rect/4, 
               str(int(tache.date_fin_tot)),
               ha='center', va='center', fontsize=15, 
               fontweight='bold', color='#1D3557', zorder=12)
        
        # Haut droite : Date au plus tard (orange)
        ax.text(x + largeur_rect/4, y + hauteur_rect/4, 
               str(int(tache.date_fin_tard)),
               ha='center', va='center', fontsize=15, 
               fontweight='bold', color='#F77F00', zorder=12)
        
        # Bas : Marge totale (cyan)
        ax.text(x, y - hauteur_rect/4, 
               str(int(tache.marge_totale)),
               ha='center', va='center', fontsize=15, 
               fontweight='bold', color='#06AED5', zorder=12)
        
        # ID À GAUCHE du nœud (au lieu d'en haut)
        id_x_offset = -largeur_rect/2 - 0.35
        label_text = f"{node_id}"
        
        ax.text(x + id_x_offset, y, label_text,
               ha='right', va='center', fontsize=16, fontweight='bold',
               color=couleur_bordure, zorder=13)
        
        # Durée À DROITE du nœud
        duree_x_offset = largeur_rect/2 + 0.35
        ax.text(x + duree_x_offset, y, f"{tache.duree}j",
               ha='left', va='center', fontsize=13, fontweight='bold',
               color='#666666', zorder=13)
    
    # Configuration des axes
    ax.axis("off")
    ax.set_title("Diagramme PERT - Ordonnancement de projet", 
                fontsize=20, fontweight='bold', pad=30, color='#1D3557')
    
    # Légende en haut à gauche
    legend_x = 0.02
    legend_y = 0.98
    
    # Titre de la légende
    ax.text(legend_x, legend_y, "Légende :", transform=ax.transAxes,
           fontsize=14, fontweight='bold', va='top', color='#1D3557')
    
    # Ligne critique
    ax.plot([legend_x, legend_x + 0.10], [legend_y - 0.04, legend_y - 0.04], 
           transform=ax.transAxes,
           color='#E63946', linewidth=4, solid_capstyle='round')
    ax.text(legend_x + 0.12, legend_y - 0.04, "Chemin critique", 
           transform=ax.transAxes, fontsize=11, va='center')
    
    # Ligne non-critique
    ax.plot([legend_x, legend_x + 0.10], [legend_y - 0.08, legend_y - 0.08], 
           transform=ax.transAxes,
           color='#457B9D', linewidth=2.5, solid_capstyle='round', alpha=0.6)
    ax.text(legend_x + 0.12, legend_y - 0.08, "Tâche non-critique", 
           transform=ax.transAxes, fontsize=11, va='center')
    
    # Légende du nœud (à droite)
    legend_node_x = 0.75
    legend_node_y = 0.98
    
    # Petit rectangle exemple
    rect_width = 0.10
    rect_height = 0.075
    rect_legend = mpatches.FancyBboxPatch(
        (legend_node_x, legend_node_y - rect_height),
        rect_width, rect_height,
        boxstyle="round,pad=0.01",
        facecolor='#E8F4F8',
        edgecolor='#457B9D',
        linewidth=2.5,
        transform=ax.transAxes,
        zorder=100
    )
    ax.add_patch(rect_legend)
    
    # Lignes de séparation
    ax.plot([legend_node_x + rect_width/2, legend_node_x + rect_width/2], 
           [legend_node_y - rect_height, legend_node_y], 
           transform=ax.transAxes, color='#457B9D', linewidth=1.5, alpha=0.5, zorder=101)
    ax.plot([legend_node_x, legend_node_x + rect_width], 
           [legend_node_y - rect_height/2, legend_node_y - rect_height/2], 
           transform=ax.transAxes, color='#457B9D', linewidth=1.5, alpha=0.5, zorder=101)
    
    # Annotations
    ax.text(legend_node_x + rect_width + 0.02, legend_node_y - rect_height * 0.25, "Date tôt", 
           transform=ax.transAxes, fontsize=10, va='center', color='#1D3557')
    ax.text(legend_node_x + rect_width + 0.02, legend_node_y - rect_height * 0.50, "Date tard", 
           transform=ax.transAxes, fontsize=10, va='center', color='#F77F00')
    ax.text(legend_node_x + rect_width + 0.02, legend_node_y - rect_height * 0.75, "Marge", 
           transform=ax.transAxes, fontsize=10, va='center', color='#06AED5')
    
    # Ajuster les limites (marges augmentées pour vertical)
    ax.margins(0.15)
    
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
            "Critique": "✓" if tache.est_critique else ""
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