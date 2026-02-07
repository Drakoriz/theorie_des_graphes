import streamlit as st
import time
import pandas as pd
from graphes_utils import (
    charger_graphe,
    dessiner_graphe,
    transformer_graphe_oriente_simple_from_df,
    ajouter_cycle_negatif
)

from graphes_parcours import (
    init_bfs,
    etape_bfs,
    init_dfs,
    etape_dfs
)

from graphes_mst import (
    init_prim,
    etape_prim,
    init_kruskal,
    etape_kruskal,
    dessiner_graphe_acm
)

from graphes_short import (
    init_dijkstra,
    etape_dijkstra,
    dessiner_graphe_dijkstra,
    init_bellman_ford,
    etape_bellman_ford,
    dessiner_graphe_bellman_ford,
    bellman_ford,
    floyd_warshall
)

from graphes_pert import (
    TachePERT,
    creer_projet_construction_maison,
    calculer_pert,
    dessiner_diagramme_pert,
    dessiner_diagramme_gantt,
    generer_tableau_pert,
    valider_taches
)

from graphes_data_manager import (
    generer_graphe_aleatoire,
    calculer_limites_aretes,
    dataframe_vers_csv_bytes,
    csv_bytes_vers_dataframe,
    valider_csv,
    charger_template_defaut,
    dataframe_vers_graphe,
    obtenir_statistiques_graphe,
    graphe_oriente_vers_dataframe
)
from style_loader import load_css


st.set_page_config(page_title="Théorie des graphes", layout="wide")

load_css()

# Initialisation des états
if "etat_algorithme" not in st.session_state:
    st.session_state.etat_algorithme = None
if "en_cours" not in st.session_state:
    st.session_state.en_cours = False
if "compteur_etapes" not in st.session_state:
    st.session_state.compteur_etapes = 0
if "historique" not in st.session_state:
    st.session_state.historique = []
if "config_modifiee" not in st.session_state:
    st.session_state.config_modifiee = False
if "df_graphe" not in st.session_state:
    st.session_state.df_graphe = None
if "graphe_modifie" not in st.session_state:
    st.session_state.graphe_modifie = False
if "section_active" not in st.session_state:
    st.session_state.section_active = "Algorithmes"
if "utiliser_donnees_personnalisees" not in st.session_state:
    st.session_state.utiliser_donnees_personnalisees = False
if "graphe_actif" not in st.session_state:
    st.session_state.graphe_actif = None
if "aretes_cycle_negatif" not in st.session_state:
    st.session_state.aretes_cycle_negatif = None


def reinitialiser_animation():
    """Réinitialise tous les états de l'animation."""
    st.session_state.etat_algorithme = None
    st.session_state.en_cours = False
    st.session_state.compteur_etapes = 0
    st.session_state.historique = []
    st.session_state.aretes_cycle_negatif = None


def reinitialiser_donnees():
    """Réinitialise les données du graphe."""
    st.session_state.df_graphe = None
    st.session_state.graphe_modifie = False


# ============================================================================
# SIDEBAR - Navigation entre sections
# ============================================================================
with st.sidebar:
    st.title("Navigation")
    
    # Boutons de navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "Algorithmes",
            use_container_width=True,
            type="primary" if st.session_state.section_active == "Algorithmes" else "secondary"
        ):
            st.session_state.section_active = "Algorithmes"
            st.rerun()
    
    with col2:
        if st.button(
            "Gestion des données",
            use_container_width=True,
            type="primary" if st.session_state.section_active == "Gestion" else "secondary"
        ):
            st.session_state.section_active = "Gestion"
            st.rerun()

    
    st.markdown("---")


# ============================================================================
# SECTION : GESTION DES DONNÉES
# ============================================================================
if st.session_state.section_active == "Gestion":
    st.title("Gestion des données")
    st.markdown("---")
    
    # ============================================================================
    # Statut des données actives
    # ============================================================================
    col_status1, col_status2 = st.columns([3, 1])
    
    with col_status1:
        if st.session_state.utiliser_donnees_personnalisees and st.session_state.df_graphe is not None:
            stats = obtenir_statistiques_graphe(st.session_state.df_graphe)
            st.subheader(f"**Données personnalisées actives** - {stats['nb_villes']} villes, {stats['nb_aretes']} arêtes")
        else:
            st.subheader("**Données par défaut actives** - Fichier **villes.csv**")
    
    with col_status2:
        if st.session_state.utiliser_donnees_personnalisees and st.session_state.df_graphe is not None:
            if st.button("Revenir aux données par défaut", use_container_width=True):
                st.session_state.utiliser_donnees_personnalisees = False
                st.session_state.graphe_actif = None
                reinitialiser_animation()
                st.rerun()
    
    st.markdown("---")
    
    # ============================================================================
    # Tabs principaux
    # ============================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Télécharger les données actuelles",
        "2. Importer vos données",
        "3. Modifier/Éditer",
        "4. Générer aléatoirement"
    ])
    
    # ============================================================================
    # TAB 1: Télécharger les données actuelles
    # ============================================================================
    with tab1:
        st.header("Télécharger les données actuelles")
        
        st.markdown("""
        Téléchargez les données actuellement utilisées par l'application.
        - Si vous utilisez des données personnalisées, vous téléchargerez ces données
        - Sinon, vous téléchargerez le fichier par défaut **villes.csv**
        """)
        
        try:
            # Déterminer quelles données télécharger
            if st.session_state.utiliser_donnees_personnalisees and st.session_state.df_graphe is not None:
                df_a_telecharger = st.session_state.df_graphe
                nom_fichier = "donnees_personnalisees.csv"
                st.write("Vous êtes sur le point de télécharger vos **données personnalisées**")
            else:
                # Données par défaut
                df_a_telecharger = charger_template_defaut()
                nom_fichier = "villes.csv"
                st.write("Vous êtes sur le point de télécharger les **données par défaut**")
            
            # Afficher un aperçu
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Aperçu des données")
                st.dataframe(df_a_telecharger, use_container_width=True)
            
            with col2:
                st.subheader("Statistiques")
                stats = obtenir_statistiques_graphe(df_a_telecharger)
                st.metric("Villes", stats['nb_villes'])
                st.metric("Arêtes", stats['nb_aretes'])
                st.metric("Distance moy.", f"{stats['distance_moyenne']:.1f} km")
                
                st.markdown("---")
                
                # Bouton de téléchargement
                csv_bytes = dataframe_vers_csv_bytes(df_a_telecharger)
                st.download_button(
                    label="Télécharger",
                    data=csv_bytes,
                    file_name=nom_fichier,
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )
        
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
    
    # ============================================================================
    # TAB 2: Importer des données personnalisées
    # ============================================================================
    with tab2:
        st.header("Importer vos données")
        
        st.markdown("""
        Importez un fichier CSV avec vos propres données de graphe.
        
        **Format requis :**
        - Séparateur : point-virgule (**;**)
        - Colonnes : **ville_a**, **ville_b**, **distance**
        - Pas de doublons
        - Pas de boucles (ville vers elle-même)
        - Graphe connexe (toutes les villes accessibles)
        """)
        
        # Upload du fichier
        fichier_upload = st.file_uploader(
            "Sélectionnez votre fichier CSV",
            type=['csv'],
            help="Le fichier doit respecter le format spécifié ci-dessus"
        )
        
        if fichier_upload is not None:
            try:
                # Lire le fichier uploadé
                df_upload = csv_bytes_vers_dataframe(fichier_upload.getvalue())
                
                # Valider le CSV
                est_valide, message = valider_csv(df_upload)
                
                if est_valide:
                    st.success(f"Validation réussie : {message}")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Aperçu des données importées")
                        st.dataframe(df_upload, use_container_width=True)
                    
                    with col2:
                        st.subheader("Statistiques")
                        stats = obtenir_statistiques_graphe(df_upload)
                        st.metric("Villes", stats['nb_villes'])
                        st.metric("Arêtes", stats['nb_aretes'])
                        st.metric("Distance min", f"{stats['distance_min']:.0f} km")
                        st.metric("Distance max", f"{stats['distance_max']:.0f} km")
                        
                        st.markdown("---")
                        
                        # Bouton pour appliquer les données
                        if st.button("Appliquer ces données", type="primary", use_container_width=True):
                            st.session_state.df_graphe = df_upload.copy()
                            st.session_state.graphe_modifie = True
                            st.session_state.utiliser_donnees_personnalisees = True
                            st.session_state.graphe_actif = dataframe_vers_graphe(df_upload)
                            reinitialiser_animation()
                            st.success("Données appliquées avec succès !")
                            st.rerun()
                    
                    # Visualisation
                    st.subheader("Visualisation du graphe")
                    try:
                        graphe_temp = dataframe_vers_graphe(df_upload)
                        fig = dessiner_graphe(graphe_temp, set(), None, None)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Erreur lors de la visualisation : {str(e)}")
                else:
                    st.error(f"Validation échouée : {message}")
                    st.warning("Corrigez les erreurs dans votre fichier et réessayez.")
                    
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {str(e)}")
        else:
            st.write("Aucun fichier sélectionné. Utilisez le bouton ci-dessus pour importer vos données.")
    
    # ============================================================================
    # TAB 3: Modifier/Éditer
    # ============================================================================
    with tab3:
        st.header("Modifier les données")
        
        st.markdown("""
        Modifiez les données en temps réel avec l'éditeur interactif.
        Vous pouvez ajouter, supprimer ou modifier des arêtes.
        """)
        
        # Choisir quelles données éditer
        if st.session_state.df_graphe is not None:
            df_a_editer = st.session_state.df_graphe.copy()
            st.write("Édition des données personnalisées en cours")
        else:
            df_a_editer = charger_template_defaut()
            st.write("Édition des données par défaut - Les modifications créeront de nouvelles données personnalisées")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Éditeur de données")
            
            # Éditeur de données
            df_edite = st.data_editor(
                df_a_editer,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "ville_a": st.column_config.TextColumn(
                        "Ville A",
                        help="Nom de la première ville",
                        required=True
                    ),
                    "ville_b": st.column_config.TextColumn(
                        "Ville B",
                        help="Nom de la deuxième ville",
                        required=True
                    ),
                    "distance": st.column_config.NumberColumn(
                        "Distance (km)",
                        help="Distance entre les deux villes (valeurs négatives autorisées pour Bellman-Ford)",
                        min_value=-10000,
                        max_value=10000,
                        required=True,
                        format="%.1f"
                    )
                },
                key="editeur_donnees"
            )
            
            # Boutons d'action
            col_btn1, col_btn2= st.columns(2)
            
            with col_btn1:
                if st.button("Valider et appliquer", type="primary", use_container_width=True):
                    # Valider les données éditées
                    est_valide, message = valider_csv(df_edite)
                    
                    if est_valide:
                        st.session_state.df_graphe = df_edite.copy()
                        st.session_state.graphe_modifie = True
                        st.session_state.utiliser_donnees_personnalisees = True
                        st.session_state.graphe_actif = dataframe_vers_graphe(df_edite)
                        reinitialiser_animation()
                        st.success("Données validées et appliquées !")
                        st.rerun()
                    else:
                        st.error(f"Validation échouée : {message}")
            
            with col_btn2:
                # Télécharger les modifications
                csv_bytes = dataframe_vers_csv_bytes(df_edite)
                st.download_button(
                    label="Télécharger",
                    data=csv_bytes,
                    file_name="donnees_modifiees.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            

        
        with col2:
            st.subheader("Informations")
            
            try:
                stats = obtenir_statistiques_graphe(df_edite)
                st.metric("Villes", stats['nb_villes'])
                st.metric("Arêtes", stats['nb_aretes'])
                st.metric("Distance min", f"{stats['distance_min']:.0f} km")
                st.metric("Distance max", f"{stats['distance_max']:.0f} km")
                st.metric("Distance moy.", f"{stats['distance_moyenne']:.1f} km")
            except:
                st.warning("Statistiques non disponibles")
            
            st.markdown("---")
            
            st.markdown("""
            **Conseils :**
            - Utilisez le bouton + pour ajouter une ligne
            - Cliquez sur × pour supprimer une ligne
            - Double-cliquez pour modifier une cellule
            """)
    
    # ============================================================================
    # TAB 4: Génération aléatoire
    # ============================================================================
    with tab4:
        st.header("Générer des données aléatoirement")
        
        st.markdown("""
        Créez un graphe aléatoire connexe en spécifiant vos paramètres.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Paramètres de génération")
            
            nb_villes = st.slider(
                "Nombre de villes",
                min_value=3,
                max_value=30,
                value=10,
                help="Nombre de sommets dans le graphe"
            )
            
            # Calculer les limites pour le nombre d'arêtes
            min_aretes, max_aretes = calculer_limites_aretes(nb_villes)
            
            st.write(f"""
            **Contraintes pour {nb_villes} villes :**
            - Minimum : {min_aretes} arêtes (graphe connexe minimal)
            - Maximum : {max_aretes} arêtes (graphe complet)
            """)
            
            nb_aretes = st.slider(
                "Nombre d'arêtes",
                min_value=min_aretes,
                max_value=max_aretes,
                value=min(min_aretes + (max_aretes - min_aretes) // 3, max_aretes),
                help="Nombre d'arêtes dans le graphe"
            )
            
            # Paramètres avancés
            with st.expander("Paramètres avancés"):
                col_a, col_b = st.columns(2)
                with col_a:
                    dist_min = st.number_input(
                        "Distance minimale (km)",
                        min_value=-1000,
                        max_value=1000,
                        value=30,
                        step=10,
                        help="Peut être négatif pour tester Bellman-Ford"
                    )
                with col_b:
                    dist_max = st.number_input(
                        "Distance maximale (km)",
                        min_value=dist_min,
                        max_value=1000,
                        value=200,
                        step=10
                    )
            
            # Bouton de génération
            if st.button("Générer le graphe", type="primary", use_container_width=True):
                try:
                    with st.spinner("Génération en cours..."):
                        df_genere = generer_graphe_aleatoire(
                            nb_villes=nb_villes,
                            nb_aretes=nb_aretes,
                            dist_min=dist_min,
                            dist_max=dist_max
                        )
                        
                        st.session_state.df_graphe = df_genere
                        st.session_state.graphe_modifie = True
                        
                    st.success(f"Graphe généré : {nb_villes} villes, {len(df_genere)} arêtes")
                    st.write("Le graphe a été généré mais pas encore appliqué. Utilisez le bouton 'Appliquer' ci-dessous.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {str(e)}")
        
        with col2:
            st.subheader("Informations")
            
            # Calcul de la densité
            if nb_villes > 1:
                densite = (nb_aretes / max_aretes) * 100
                st.metric("Densité", f"{densite:.1f}%")
                
                if densite < 30:
                    st.write("[Faible] Graphe épars")
                elif densite < 70:
                    st.write("[Moyen] Graphe moyennement dense")
                else:
                    st.write("[Élevé] Graphe dense")
            
            st.markdown("---")
            
            st.markdown("""
            **Conseils :**
            - Graphe épars : plus facile à visualiser
            - Graphe dense : plus complexe
            - Pour débuter : 5-10 villes
            """)
        
        # Afficher le graphe généré s'il existe
        if st.session_state.df_graphe is not None and st.session_state.graphe_modifie:
            st.markdown("---")
            st.subheader("Aperçu du graphe généré")
            
            col_preview1, col_preview2 = st.columns([2, 1])
            
            with col_preview1:
                st.dataframe(st.session_state.df_graphe, use_container_width=True)
                
                # Visualisation
                try:
                    graphe_temp = dataframe_vers_graphe(st.session_state.df_graphe)
                    fig = dessiner_graphe(graphe_temp, set(), None, None)
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"Erreur lors de la visualisation : {str(e)}")
            
            with col_preview2:
                stats = obtenir_statistiques_graphe(st.session_state.df_graphe)
                st.metric("Villes", stats['nb_villes'])
                st.metric("Arêtes", stats['nb_aretes'])
                st.metric("Distance min", f"{stats['distance_min']:.0f} km")
                st.metric("Distance max", f"{stats['distance_max']:.0f} km")
                
                st.markdown("---")
                
                # Bouton pour appliquer
                if st.button("Appliquer ces données", type="primary", use_container_width=True, key="appliquer_random"):
                    st.session_state.utiliser_donnees_personnalisees = True
                    st.session_state.graphe_actif = dataframe_vers_graphe(st.session_state.df_graphe)
                    reinitialiser_animation()
                    st.success("Données appliquées !")
                    st.rerun()
                
                # Téléchargement
                csv_bytes = dataframe_vers_csv_bytes(st.session_state.df_graphe)
                st.download_button(
                    label="Télécharger",
                    data=csv_bytes,
                    file_name="graphe_genere.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # ============================================================================
    # Footer de la section
    # ============================================================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Projet : Algorithmes de graphes</strong></p>
        <p>Un projet réalisé par William WAN & Hsiao-Wen-Paul LO</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# SECTION : ALGORITHMES (section principale originale)
# ============================================================================
elif st.session_state.section_active == "Algorithmes":
    # Interface principale
    st.title("Théorie des graphes")
    st.markdown("---")
    
    # Configuration dans la sidebar
    with st.sidebar:
        st.subheader("Configuration")
        
        # Choix de la catégorie d'algorithme
        categorie = st.radio(
            "Catégorie d'algorithme",
            [
                "Parcours (BFS/DFS)", 
                "Arbre Couvrant Minimum", 
                "Plus Courts Chemins",
                "Chemins Avancés",
                "Ordonnancement PERT"
            ],
            key="categorie"
        )
    
    # Chargement du graphe (données personnalisées ou par défaut)
    # Ne pas afficher pour PERT car il n'utilise pas le graphe
    if categorie != "Ordonnancement PERT":
        if st.session_state.utiliser_donnees_personnalisees and st.session_state.graphe_actif is not None:
            graphe = st.session_state.graphe_actif
            df_graphe_actuel = st.session_state.df_graphe
            col_info1, col_info2 = st.columns([4, 1])
            with col_info1:
                stats = obtenir_statistiques_graphe(st.session_state.df_graphe)
                st.subheader(f"Utilisation des données personnalisées - {stats['nb_villes']} villes, {stats['nb_aretes']} arêtes")
            with col_info2:
                if st.button("Changer", use_container_width=True):
                    st.session_state.section_active = "Gestion"
                    st.rerun()
            st.markdown("---")
        else:
            graphe = charger_graphe("villes.csv")
            df_graphe_actuel = charger_template_defaut()
            col_info1, col_info2 = st.columns([4, 1])
            with col_info1:
                st.subheader("Utilisation des données par défaut (villes.csv)")
            with col_info2:
                if st.button("Changer", use_container_width=True):
                    st.session_state.section_active = "Gestion"
                    st.rerun()
            st.markdown("---")
    else:
        # Pour PERT, créer un graphe vide (non utilisé)
        graphe = {}
        df_graphe_actuel = None
    
    # Configuration dans la sidebar (suite)
    with st.sidebar:
        
        if categorie == "Parcours (BFS/DFS)":
            algo = st.radio("Algorithme", ["BFS", "DFS"], key="algo")
            noeud_depart = st.selectbox("Ville de départ", list(sorted(graphe.keys())), key="depart")
            noeud_arrivee = None
            
        elif categorie == "Arbre Couvrant Minimum":
            algo = st.radio("Algorithme", ["Prim", "Kruskal"], key="algo")
            if algo == "Prim":
                noeud_depart = st.selectbox("Ville de départ", list(sorted(graphe.keys())), key="depart")
            else:
                noeud_depart = None
            noeud_arrivee = None
            
        elif categorie == "Plus Courts Chemins":
            algo = "Dijkstra"
            noeud_depart = st.selectbox("Ville de départ", list(sorted(graphe.keys())), key="depart")
            noeud_arrivee = st.selectbox("Ville d'arrivée", list(sorted(graphe.keys())), key="arrivee")
            
        elif categorie == "Chemins Avancés":
            algo = st.radio("Algorithme", ["Bellman-Ford", "Floyd-Warshall"], key="algo")
            if algo == "Bellman-Ford":
                noeud_depart = st.selectbox("Ville de départ", list(sorted(graphe.keys())), key="depart")
                noeud_arrivee = None
                
                # Options spéciales pour Bellman-Ford
                st.markdown("---")
                st.markdown("**Options Bellman-Ford**")
                
                # Option 1 : Graphe orienté (toujours disponible)
                graphe_oriente = st.checkbox(
                    "Transformer en graphe orienté (ville_a → ville_b)",
                    value=False,
                    help="Convertit le graphe en version orientée : chaque arête devient ville_a → ville_b"
                )
                
                # Option 2 : Cycle négatif (seulement si données par défaut ET graphe orienté)
                if not st.session_state.utiliser_donnees_personnalisees and graphe_oriente:
                    cycle_negatif = st.checkbox(
                        "Créer un cycle négatif",
                        value=False,
                        help="Crée un cycle négatif dans le graphe pour tester la détection"
                    )
                else:
                    cycle_negatif = False
                
            else:
                noeud_depart = None
                noeud_arrivee = None
                graphe_oriente = False
                cycle_negatif = False
                
        else:  # Ordonnancement PERT
            algo = "PERT"
            noeud_depart = None
            noeud_arrivee = None
            graphe_oriente = False
            cycle_negatif = False
        
        # Reset si l'algorithme change pendant une exécution
        if st.session_state.etat_algorithme is not None:
            if algo == "BFS" and "file" not in st.session_state.etat_algorithme:
                reinitialiser_animation()
                st.rerun()
            elif algo == "DFS" and "pile" not in st.session_state.etat_algorithme:
                reinitialiser_animation()
                st.rerun()
            elif algo == "Prim" and "file_priorite" not in st.session_state.etat_algorithme:
                reinitialiser_animation()
                st.rerun()
            elif algo == "Kruskal" and "uf" not in st.session_state.etat_algorithme:
                reinitialiser_animation()
                st.rerun()
            elif algo == "Dijkstra" and "depart" not in st.session_state.etat_algorithme:
                reinitialiser_animation()
                st.rerun()
            elif algo == "Bellman-Ford" and "aretes" not in st.session_state.etat_algorithme:
                reinitialiser_animation()
                st.rerun()
        
        if categorie not in ["Ordonnancement PERT"]:
            # Floyd-Warshall n'a pas de slider de vitesse
            if algo != "Floyd-Warshall":
                vitesse = st.slider("Vitesse (ms)", 100, 2000, 500, 100, key="vitesse")
        
        st.markdown("---")
        
        # Appliquer les transformations pour Bellman-Ford
        if algo == "Bellman-Ford":
            graphe_original = graphe.copy()
            
            # Transformation 1 : Graphe orienté
            if graphe_oriente:
                graphe = transformer_graphe_oriente_simple_from_df(df_graphe_actuel)
                st.info("Graphe transformé en orienté (ville_a → ville_b)")
            
            # Transformation 2 : Cycle négatif (seulement données par défaut + graphe orienté)
            if cycle_negatif and graphe_oriente and not st.session_state.utiliser_donnees_personnalisees:
                graphe_avec_cycle, aretes_cycle = ajouter_cycle_negatif(graphe)
                if graphe_avec_cycle:
                    graphe = graphe_avec_cycle
                    st.session_state.aretes_cycle_negatif = aretes_cycle
                    st.error("Un cycle négatif a été créé dans le graphe")
                else:
                    st.session_state.aretes_cycle_negatif = None
                    st.warning("Impossible de créer un cycle négatif dans ce graphe")
            else:
                st.session_state.aretes_cycle_negatif = None
        
        st.markdown("---")
        
        # Boutons de contrôle
        if categorie not in ["Ordonnancement PERT"]:
            # Pour Floyd-Warshall, on garde un bouton simple d'exécution
            if algo == "Floyd-Warshall":
                pass  # Sera géré dans la section spécifique
            else:
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("Démarrer", use_container_width=True, type="primary", disabled=st.session_state.en_cours):
                        if algo == "BFS":
                            st.session_state.etat_algorithme = init_bfs(graphe, noeud_depart)
                        elif algo == "DFS":
                            st.session_state.etat_algorithme = init_dfs(graphe, noeud_depart)
                        elif algo == "Prim":
                            st.session_state.etat_algorithme = init_prim(graphe, noeud_depart)
                        elif algo == "Kruskal":
                            st.session_state.etat_algorithme = init_kruskal(graphe)
                        elif algo == "Dijkstra":
                            st.session_state.etat_algorithme = init_dijkstra(graphe, noeud_depart, noeud_arrivee)
                        elif algo == "Bellman-Ford":
                            st.session_state.etat_algorithme = init_bellman_ford(graphe, noeud_depart)
                        st.session_state.en_cours = True
                        st.session_state.compteur_etapes = 0
                        st.session_state.historique = []
                
                with col_btn2:
                    if st.button("Reset", use_container_width=True):
                        reinitialiser_animation()
                        st.rerun()
                
                label_pause = "Pause" if st.session_state.en_cours else "Reprendre"
                if st.button(label_pause, use_container_width=True, disabled=st.session_state.etat_algorithme is None):
                    st.session_state.en_cours = not st.session_state.en_cours
                    st.rerun()
        
        st.markdown("---")
        
        with st.expander("À propos des algorithmes"):
            if categorie == "Parcours (BFS/DFS)":
                st.markdown("""
                **BFS (Breadth-First Search)**  
                Parcourt le graphe niveau par niveau en utilisant une file (FIFO).
                Garantit de trouver le chemin le plus court en nombre d'arêtes.
                
                **DFS (Depth-First Search)**  
                Parcourt le graphe en profondeur en utilisant une pile (LIFO).
                Explore un chemin jusqu'au bout avant de revenir en arrière.
                """)
            elif categorie == "Arbre Couvrant Minimum":
                st.markdown("""
                **Prim**  
                Construit l'arbre couvrant minimum en partant d'un sommet et en ajoutant 
                à chaque étape l'arête de poids minimum qui connecte l'arbre à un nouveau sommet.
                
                **Kruskal**  
                Trie toutes les arêtes par poids croissant et les ajoute une par une, 
                en évitant de créer des cycles.
                """)
            elif categorie == "Plus Courts Chemins":
                st.markdown("""
                **Dijkstra**  
                Trouve le plus court chemin entre deux sommets dans un graphe à poids positifs.
                Utilise une file de priorité pour explorer les sommets par distance croissante.
                """)
            elif categorie == "Chemins Avancés":
                st.markdown("""
                **Bellman-Ford**  
                Trouve les plus courts chemins même avec des poids négatifs.
                Détecte également les cycles négatifs.
                
                **Floyd-Warshall**  
                Calcule tous les plus courts chemins entre toutes les paires de sommets.
                """)
            else:
                st.markdown("""
                **Méthode PERT**  
                Permet d'ordonnancer des tâches dépendantes et d'identifier le chemin critique
                d'un projet (ensemble de tâches sans marge).
                """)
    
    # Contenu principal
    if categorie == "Chemins Avancés":
        st.header(f"Algorithme : {algo}")
        
        if algo == "Bellman-Ford":
            st.markdown("""
            L'algorithme de Bellman-Ford calcule les plus courts chemins depuis un sommet source,
            même en présence de poids négatifs. Il détecte également les cycles négatifs.
            
            **Principe :** Relaxer toutes les arêtes |V|-1 fois, puis vérifier les cycles négatifs.
            """)
            
            # Affichage identique à BFS/DFS/Dijkstra
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("Graphe")
                
                if st.session_state.etat_algorithme:
                    etat = st.session_state.etat_algorithme
                    
                    # Dessiner le graphe
                    fig = dessiner_graphe_bellman_ford(
                        graphe,
                        etat["distances"],
                        etat["predecesseurs"],
                        etat["depart"],
                        etat.get("aretes_relaxees", []),
                        st.session_state.aretes_cycle_negatif
                    )
                    st.pyplot(fig)
                else:
                    # Afficher le graphe initial même avant le lancement
                    # Créer un état initial pour l'affichage
                    distances_init = {sommet: float('inf') for sommet in graphe}
                    distances_init[noeud_depart] = 0
                    predecesseurs_init = {sommet: None for sommet in graphe}
                    
                    fig = dessiner_graphe_bellman_ford(
                        graphe,
                        distances_init,
                        predecesseurs_init,
                        noeud_depart,
                        [],
                        st.session_state.aretes_cycle_negatif
                    )
                    st.pyplot(fig)
                
                # Légende
                # Construire la légende HTML
                legende_parts = [
                    "<div style='display: flex; gap: 15px; justify-content: center; margin-top: 10px; flex-wrap: wrap;'>",
                    "<div style='display: flex; align-items: center; gap: 5px;'>",
                    "<span style='display: inline-block; width: 14px; height: 14px; background: #007AFF; border: 2px solid black; border-radius: 50%;'></span>",
                    "<span style='color: #1a1a1a;'>Départ</span>",
                    "</div>",
                    "<div style='display: flex; align-items: center; gap: 5px;'>",
                    "<span style='display: inline-block; width: 14px; height: 14px; background: #13C266; border: 2px solid black; border-radius: 50%;'></span>",
                    "<span style='color: #1a1a1a;'>Atteignable</span>",
                    "</div>",
                    "<div style='display: flex; align-items: center; gap: 5px;'>",
                    "<span style='display: inline-block; width: 30px; height: 3px; background: #13C266;'></span>",
                    "<span style='color: #1a1a1a;'>Arbre des chemins</span>",
                    "</div>",
                    "<div style='display: flex; align-items: center; gap: 5px;'>",
                    "<span style='display: inline-block; width: 30px; height: 3px; background: #B0152A;'></span>",
                    "<span style='color: #1a1a1a;'>Arête relaxée</span>",
                    "</div>",
                    "<div style='display: flex; align-items: center; gap: 5px;'>",
                    "<span style='display: inline-block; width: 30px; height: 2px; background: #FF9500; border-top: 1px dashed #FF9500;'></span>",
                    "<span style='color: #1a1a1a;'>Poids négatif</span>",
                    "</div>"
                ]
                
                # Ajouter la légende du cycle négatif si présent
                if st.session_state.aretes_cycle_negatif:
                    legende_parts.extend([
                        "<div style='display: flex; align-items: center; gap: 5px;'>",
                        "<span style='display: inline-block; width: 30px; height: 3px; background: #9B59B6;'></span>",
                        "<span style='color: #1a1a1a;'>Cycle négatif</span>",
                        "</div>"
                    ])
                
                legende_parts.append("</div>")
                legende_html = "".join(legende_parts)
                st.markdown(legende_html, unsafe_allow_html=True)
            
            with col2:
                st.subheader("Informations")
                
                if st.session_state.etat_algorithme:
                    etat = st.session_state.etat_algorithme
                    
                    st.markdown(f"### État actuel (Itération {etat['iteration_courante']})")
                    
                    st.markdown(f"**Départ :** `{etat['depart']}`")
                    st.markdown(f"**Itération :** `{etat['iteration_courante']} / {etat['nb_iterations_max']}`")
                    
                    if etat.get("termine", False):
                        if etat.get("cycle_negatif", False):
                            st.error("Cycle négatif détecté")
                        else:
                            st.write("**Algorithme terminé**")
                            st.write("Aucun cycle négatif détecté")
                        st.session_state.en_cours = False
                    
                    # Tableau Node / Cost / Previous
                    st.markdown("#### Tableau des distances")
                    
                    tableau_data = []
                    for node in graphe.keys():
                        dist = etat["distances"][node]
                        pred = etat["predecesseurs"][node]
                        
                        tableau_data.append({
                            "Node": node,
                            "Cost": dist,  # Garder la valeur numérique pour le tri
                            "Cost_Display": f"{dist:.0f}" if dist != float('inf') else "∞",
                            "Previous": pred if pred else "-"
                        })
                    
                    # Trier par coût (les infinis à la fin)
                    tableau_data.sort(key=lambda x: (x["Cost"] == float('inf'), x["Cost"]))
                    
                    # Créer le DataFrame avec seulement les colonnes d'affichage
                    df_tableau = pd.DataFrame([
                        {
                            "Node": item["Node"],
                            "Cost": item["Cost_Display"],
                            "Previous": item["Previous"]
                        }
                        for item in tableau_data
                    ])
                    
                    st.dataframe(df_tableau, use_container_width=True, hide_index=True)
                    
                    # Arêtes relaxées à cette itération
                    if etat.get("aretes_relaxees"):
                        st.markdown("#### Arêtes relaxées")
                        for u, v, old_dist, new_dist in etat["aretes_relaxees"]:
                            old_str = f"{old_dist:.0f}" if old_dist != float('inf') else "∞"
                            st.markdown(f"- **{u} → {v}** : {old_str} → {new_dist:.0f}")
                else:
                    st.write("Veuillez lancer le programme.")
                
                # Historique
                if st.session_state.historique:
                    with st.expander(f"Historique des itérations ({len(st.session_state.historique)} itérations)", expanded=False):
                        for info_etape in st.session_state.historique:
                            if info_etape.get("type") == "iteration":
                                st.markdown(f"""
                                **Itération {info_etape['iteration']}**
                                """)
                                if info_etape.get("aretes_relaxees"):
                                    for u, v, old_dist, new_dist in info_etape["aretes_relaxees"]:
                                        old_str = f"{old_dist:.0f}" if old_dist != float('inf') else "∞"
                                        st.markdown(f"- {u} → {v} : {old_str} → {new_dist:.0f}")
                                else:
                                    st.markdown("- Aucune arête relaxée")
                            elif info_etape.get("type") == "verification_cycle":
                                st.markdown(f"""
                                **Vérification des cycles négatifs**
                                """)
                                if info_etape.get("cycle_negatif"):
                                    st.error("Cycle négatif détecté !")
                                else:
                                    st.success("Aucun cycle négatif")
                            st.divider()
        
        else:  # Floyd-Warshall
            st.markdown("""
            L'algorithme de Floyd-Warshall calcule tous les plus courts chemins entre
            toutes les paires de sommets du graphe.
            """)
            
            if st.button("Exécuter Floyd-Warshall", type="primary"):
                with st.spinner("Calcul en cours..."):
                    distances, predecesseurs, etapes = floyd_warshall(graphe)
                
                st.subheader("Matrice des distances")
                
                # Créer une matrice de distances pour affichage
                villes = sorted(list(graphe.keys()))
                matrice_df = pd.DataFrame(
                    [[f"{distances[i][j]:.0f}" if distances[i][j] != float('inf') else "∞" 
                      for j in villes] for i in villes],
                    index=villes,
                    columns=villes
                )
                
                st.dataframe(matrice_df, use_container_width=True)
                
                # Analyse de centralité
                st.subheader("Analyse de centralité")
                
                centralites = {}
                for ville in villes:
                    somme_distances = sum(distances[ville][autre] 
                                        for autre in villes 
                                        if distances[ville][autre] != float('inf') and ville != autre)
                    nb_accessibles = sum(1 for autre in villes 
                                       if distances[ville][autre] != float('inf') and ville != autre)
                    
                    if nb_accessibles > 0:
                        centralites[ville] = somme_distances / nb_accessibles
                    else:
                        centralites[ville] = float('inf')
                
                # Ville la plus centrale (distance moyenne minimale)
                ville_centrale = min(centralites.items(), key=lambda x: x[1])
                
                st.write(f"""
                **Ville la plus centrale :** {ville_centrale[0]}
                
                Distance moyenne vers les autres villes : {ville_centrale[1]:.1f} km
                """)
    
    elif categorie == "Ordonnancement PERT":
        st.header("Méthode PERT - Ordonnancement de Projet")
        
        st.markdown("""
        La méthode PERT (Program Evaluation and Review Technique) permet de :
        - Modéliser un projet avec des tâches dépendantes
        - Calculer les dates au plus tôt et au plus tard
        - Identifier le chemin critique (tâches sans marge)
        - Visualiser avec des diagrammes PERT et Gantt
        """)
        
        st.markdown("---")
        
        # Initialisation de l'état PERT
        if "taches_pert" not in st.session_state:
            st.session_state.taches_pert = None
        if "projet_selectionne" not in st.session_state:
            st.session_state.projet_selectionne = None
        
        # Choix du projet
        st.subheader("Définir votre projet")
        
        col_choix1, col_choix2 = st.columns([3, 1])
        
        with col_choix1:
            mode_projet = st.radio(
                "Comment souhaitez-vous définir votre projet ?",
                [
                    "Définir mon propre projet (recommandé pour le rapport)",
                    "Utiliser l'exemple 'Construction d'une maison' (12 tâches)"
                ],
                key="mode_projet_pert"
            )
        
        with col_choix2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Initialiser", type="primary", use_container_width=True):
                if "propre projet" in mode_projet:
                    # Projet vide pour personnalisation
                    st.session_state.taches_pert = []
                    st.session_state.projet_selectionne = "Mon projet"
                else:
                    # Exemple construction maison
                    st.session_state.taches_pert = creer_projet_construction_maison()
                    st.session_state.projet_selectionne = "Construction d'une maison"
                st.rerun()
        
        st.markdown("---")
        
        # Si un projet est chargé
        if st.session_state.taches_pert is not None:
            
            # Tabs pour organiser l'interface
            tab1, tab2, tab3, tab4 = st.tabs([
                " Définition des tâches",
                " Calculs PERT",
                " Diagramme PERT",
                " Diagramme de Gantt"
            ])
            
            # ============================================================================
            # TAB 1 : Définition des tâches
            # ============================================================================
            with tab1:
                st.subheader(f"Projet : {st.session_state.projet_selectionne}")
                
                if st.session_state.projet_selectionne == "Mon projet":
                    st.info("""
                     **Conseil pour le rapport :** Créez un projet pertinent lié aux graphes.
                    
                    **Exemples d'idées :**
                    - Construction d'une infrastructure
                    - Organisation d'un projet événementiel
                    - Développement d'un logiciel
                    - Planification d'une campagne marketing
                    """)
                
                # Formulaire d'ajout de tâche - TOUJOURS affiché
                with st.expander(" Ajouter une nouvelle tâche", expanded=len(st.session_state.taches_pert) == 0):
                    st.markdown("**Définissez une nouvelle tâche pour votre projet**")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        id_tache = st.text_input(
                            "ID de la tâche",
                            value="",
                            max_chars=3,
                            help="Ex: A, B, C ou T1, T2, T3",
                            key="new_id"
                        )
                    
                    with col2:
                        nom_tache = st.text_input(
                            "Nom de la tâche",
                            value="",
                            help="Ex: 'Étude de faisabilité', 'Installation équipements'",
                            key="new_nom"
                        )
                    
                    col3, col4 = st.columns([1, 2])
                    
                    with col3:
                        duree_tache = st.number_input(
                            "Durée (jours)",
                            min_value=1,
                            value=5,
                            help="Durée estimée de la tâche en jours",
                            key="new_duree"
                        )
                    
                    with col4:
                        # Récupérer les IDs existants pour le selectbox
                        ids_existants = [t.id for t in st.session_state.taches_pert]
                        
                        if ids_existants:
                            dependances_selectionnees = st.multiselect(
                                "Dépendances (tâches à terminer avant)",
                                options=ids_existants,
                                help="Sélectionnez les tâches qui doivent être terminées avant celle-ci",
                                key="new_deps"
                            )
                        else:
                            st.text_input(
                                "Dépendances",
                                value="",
                                disabled=True,
                                help="Aucune tâche existante. Cette sera la première.",
                                key="new_deps_disabled"
                            )
                            dependances_selectionnees = []
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
                    
                    with col_btn1:
                        if st.button(" Ajouter cette tâche", type="primary", use_container_width=True):
                            if id_tache and nom_tache:
                                # Vérifier que l'ID n'existe pas déjà
                                if any(t.id == id_tache for t in st.session_state.taches_pert):
                                    st.error(f" L'ID '{id_tache}' existe déjà !")
                                else:
                                    nouvelle_tache = TachePERT(id_tache, nom_tache, duree_tache, dependances_selectionnees)
                                    st.session_state.taches_pert.append(nouvelle_tache)
                                    st.success(f" Tâche {id_tache} : {nom_tache} ajoutée !")
                                    st.rerun()
                            else:
                                st.error(" Veuillez remplir au moins l'ID et le nom de la tâche.")
                    
                    with col_btn2:
                        if st.session_state.taches_pert and st.session_state.projet_selectionne == "Mon projet":
                            if st.button(" Tout effacer", use_container_width=True):
                                st.session_state.taches_pert = []
                                st.rerun()
                    
                    with col_btn3:
                        pass  # Espacement
                
                st.markdown("---")
                
                # Affichage des tâches existantes
                if st.session_state.taches_pert:
                    st.markdown("###  Liste des tâches définies")
                    
                    taches_data = []
                    for tache in st.session_state.taches_pert:
                        taches_data.append({
                            "ID": tache.id,
                            "Nom": tache.nom,
                            "Durée (j)": tache.duree,
                            "Dépendances": ", ".join(tache.dependances) if tache.dependances else "-"
                        })
                    
                    df_taches = pd.DataFrame(taches_data)
                    st.dataframe(df_taches, use_container_width=True, hide_index=True)
                    
                    # Bouton de suppression individuelle
                    if st.session_state.projet_selectionne == "Mon projet":
                        with st.expander(" Supprimer une tâche"):
                            col_del1, col_del2 = st.columns([3, 1])
                            with col_del1:
                                id_a_supprimer = st.selectbox(
                                    "Sélectionner la tâche à supprimer",
                                    [""] + [f"{t.id} - {t.nom}" for t in st.session_state.taches_pert],
                                    key="del_id"
                                )
                            with col_del2:
                                st.write("")  # Spacing
                                if st.button("Supprimer", type="secondary", use_container_width=True):
                                    if id_a_supprimer:
                                        id_seul = id_a_supprimer.split(" - ")[0]
                                        st.session_state.taches_pert = [
                                            t for t in st.session_state.taches_pert 
                                            if t.id != id_seul
                                        ]
                                        st.success(f" Tâche {id_seul} supprimée !")
                                        st.rerun()
                else:
                    st.info(" Aucune tâche définie. Ajoutez votre première tâche ci-dessus pour commencer.")
            
            # ============================================================================
            # TAB 2 : Calculs PERT
            # ============================================================================
            with tab2:
                if st.session_state.taches_pert:
                    # Valider les tâches
                    valide, message = valider_taches(st.session_state.taches_pert)
                    
                    if not valide:
                        st.error(f" Erreur de validation : {message}")
                    else:
                        st.success(" Projet valide et prêt pour les calculs PERT")
                        
                        if st.button(" Lancer les calculs PERT", type="primary"):
                            with st.spinner("Calculs en cours..."):
                                # Calculer PERT
                                taches_dict, chemin_critique, duree_projet = calculer_pert(
                                    st.session_state.taches_pert
                                )
                                
                                # Stocker dans session_state
                                st.session_state.pert_calcule = True
                                st.session_state.chemin_critique = chemin_critique
                                st.session_state.duree_projet = duree_projet
                                
                                st.rerun()
                        
                        # Afficher les résultats si calculés
                        if hasattr(st.session_state, 'pert_calcule') and st.session_state.pert_calcule:
                            st.markdown("---")
                            
                            # Métriques principales
                            col_m1, col_m2, col_m3 = st.columns(3)
                            
                            with col_m1:
                                st.metric(" Durée totale du projet", f"{st.session_state.duree_projet:.0f} jours")
                            with col_m2:
                                st.metric(" Nombre de tâches", len(st.session_state.taches_pert))
                            with col_m3:
                                st.metric(" Tâches critiques", len(st.session_state.chemin_critique))
                            
                            st.markdown("---")
                            
                            # Chemin critique
                            st.subheader(" Chemin critique")
                            taches_critiques = [
                                t for t in st.session_state.taches_pert 
                                if t.id in st.session_state.chemin_critique
                            ]
                            
                            chemin_str = " → ".join([f"{t.id} ({t.nom})" for t in taches_critiques])
                            st.markdown(f"**{chemin_str}**")
                            
                            st.info("""
                             **Le chemin critique** représente la séquence de tâches qui détermine 
                            la durée minimale du projet. Tout retard sur ces tâches retarde l'ensemble du projet.
                            """)
                            
                            st.markdown("---")
                            
                            # Tableau détaillé
                            st.subheader(" Tableau récapitulatif PERT")
                            
                            tableau = generer_tableau_pert(st.session_state.taches_pert)
                            df_pert = pd.DataFrame(tableau)
                            
                            # Styler le tableau
                            st.dataframe(
                                df_pert,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            st.markdown("""
                            **Légende :**
                            - **Début tôt / Fin tôt** : Dates au plus tôt (quand on peut commencer/finir au plus tôt)
                            - **Début tard / Fin tard** : Dates au plus tard (quand on doit commencer/finir au plus tard)
                            - **Marge totale** : Retard possible sans retarder le projet
                            - **Marge libre** : Retard possible sans retarder les tâches suivantes
                            - **Critique** : Tâche sur le chemin critique (marge = 0)
                            """)
                else:
                    st.info("Aucune tâche définie. Allez dans l'onglet 'Définition des tâches'.")
            
            # ============================================================================
            # TAB 3 : Diagramme PERT
            # ============================================================================
            with tab3:
                if hasattr(st.session_state, 'pert_calcule') and st.session_state.pert_calcule:
                    st.subheader(" Diagramme PERT")
                    
                    st.info("""
                    Le diagramme PERT visualise les dépendances entre tâches. 
                    Les tâches **rouges** sont sur le chemin critique, les **vertes** ont de la marge.
                    """)
                    
                    with st.spinner("Génération du diagramme..."):
                        fig_pert = dessiner_diagramme_pert(
                            st.session_state.taches_pert,
                            st.session_state.chemin_critique
                        )
                        st.pyplot(fig_pert)
                    
                    # Légende
                    st.markdown("""
                    **Légende :**
                    - **Nœuds rouges** : Tâches critiques (aucune marge)
                    - **Nœuds verts** : Tâches non-critiques (avec marge)
                    - **Flèches rouges** : Dépendances sur le chemin critique
                    - **Flèches grises** : Autres dépendances
                    """)
                else:
                    st.warning(" Veuillez d'abord lancer les calculs PERT dans l'onglet 'Calculs PERT'.")
            
            # ============================================================================
            # TAB 4 : Diagramme de Gantt
            # ============================================================================
            with tab4:
                if hasattr(st.session_state, 'pert_calcule') and st.session_state.pert_calcule:
                    st.subheader(" Diagramme de Gantt")
                    
                    st.info("""
                    Le diagramme de Gantt montre la planification temporelle du projet.
                    Les barres **rouges** sont critiques, les **vertes** ont de la marge (en gris clair).
                    """)
                    
                    with st.spinner("Génération du diagramme..."):
                        fig_gantt = dessiner_diagramme_gantt(
                            st.session_state.taches_pert,
                            st.session_state.chemin_critique
                        )
                        st.pyplot(fig_gantt)
                    
                    # Légende
                    st.markdown("""
                    **Légende :**
                    - **Barres rouges** : Tâches critiques
                    - **Barres vertes** : Tâches non-critiques
                    - **Zones grises** : Marge disponible
                    """)
                    
                    # Export/Download
                    st.markdown("---")
                    st.markdown("###  Export")
                    
                    col_exp1, col_exp2 = st.columns(2)
                    
                    with col_exp1:
                        # Export tableau CSV
                        tableau = generer_tableau_pert(st.session_state.taches_pert)
                        df_export = pd.DataFrame(tableau)
                        csv = df_export.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=" Télécharger le tableau PERT (CSV)",
                            data=csv,
                            file_name=f"pert_{st.session_state.projet_selectionne.replace(' ', '_')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col_exp2:
                        st.info("Les diagrammes peuvent être téléchargés via le bouton de téléchargement sur les graphiques.")
                
                else:
                    st.warning(" Veuillez d'abord lancer les calculs PERT dans l'onglet 'Calculs PERT'.")
        
        else:
            st.info(" Choisissez un projet ci-dessus et cliquez sur 'Charger le projet' pour commencer.")
    
    else:
        # Affichage pour les algorithmes avec animation
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Visualisation")
            
            if st.session_state.etat_algorithme and isinstance(st.session_state.etat_algorithme, dict):
                etat = st.session_state.etat_algorithme
                
                if categorie == "Parcours (BFS/DFS)":
                    # Déterminer les nœuds en file/pile
                    if "file" in etat:
                        en_file = set(etat["file"])
                    elif "pile" in etat:
                        en_file = set(etat["pile"])
                    else:
                        en_file = set()
                    
                    if "visites" in etat and "courant" in etat:
                        fig = dessiner_graphe(graphe, etat["visites"], etat["courant"], en_file)
                        st.pyplot(fig)
                    else:
                        st.warning("État de l'algorithme incomplet. Veuillez cliquer sur Reset.")
                    
                elif categorie == "Arbre Couvrant Minimum":
                    sommet_courant = etat.get("sommet_courant", None)
                    arbre = etat.get("arbre", [])
                    fig = dessiner_graphe_acm(graphe, arbre, sommet_courant)
                    st.pyplot(fig)
                    
                elif categorie == "Plus Courts Chemins":
                    # Uniquement pour Dijkstra (Bellman-Ford est dans "Chemins Avancés")
                    chemin = etat.get("chemin_trouve", []) if etat.get("termine", False) else []
                    if "visites" in etat:  # Vérifier que c'est bien Dijkstra
                        fig = dessiner_graphe_dijkstra(
                            graphe, 
                            etat["visites"], 
                            etat.get("sommet_courant"),
                            chemin,
                            etat["depart"],
                            etat["arrivee"]
                        )
                        st.pyplot(fig)
                    else:
                        st.warning("État de l'algorithme incomplet. Veuillez cliquer sur Reset.")
            else:
                fig = dessiner_graphe(graphe, set(), None, None)
                st.pyplot(fig)
            
            # Légende
            if categorie == "Parcours (BFS/DFS)":
                st.markdown("""
                <div style='display: flex; gap: 15px; justify-content: center; margin-top: 10px; flex-wrap: wrap;'>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #B0152A; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Nœud courant</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #FF9500; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>En file/pile</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #13C266; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Visité</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: white; border: 2.5px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Non visité</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif categorie == "Arbre Couvrant Minimum":
                st.markdown("""
                <div style='display: flex; gap: 15px; justify-content: center; margin-top: 10px; flex-wrap: wrap;'>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #B0152A; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Sommet courant</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #13C266; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Dans l'arbre</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 30px; height: 3px; background: #13C266;'></span>
                        <span style='color: #1a1a1a;'>Arête de l'arbre</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:  # Plus Courts Chemins
                st.markdown("""
                <div style='display: flex; gap: 15px; justify-content: center; margin-top: 10px; flex-wrap: wrap;'>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #007AFF; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Départ</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #FF2D55; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Arrivée</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #B0152A; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Sommet courant</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 14px; height: 14px; background: #13C266; border: 2px solid black; border-radius: 50%;'></span>
                        <span style='color: #1a1a1a;'>Visité</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 5px;'>
                        <span style='display: inline-block; width: 30px; height: 3px; background: #13C266;'></span>
                        <span style='color: #1a1a1a;'>Chemin optimal</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Informations")
            
            if st.session_state.etat_algorithme:
                etat = st.session_state.etat_algorithme
                
                st.markdown(f"### État actuel (Étape {st.session_state.compteur_etapes})")
                
                if algo in ["BFS", "DFS"]:
                    st.markdown(f"**Sommet courant :** {etat['courant']}")
                    
                    if "file" in etat:
                        st.markdown(f"**File d'attente :** {list(etat['file'])}")
                    elif "pile" in etat:
                        st.markdown(f"**Pile :** {etat['pile']}")
                    
                    st.markdown(f"**Visités :** {list(etat['visites'])}")  # Ordre chronologique
                    
                    if etat["termine"]:
                        st.write("Parcours terminé !")
                        st.session_state.en_cours = False
                        
                elif algo == "Prim":
                    st.markdown(f"**Sommet courant :** `{etat.get('sommet_courant', 'N/A')}`")
                    st.markdown(f"**Sommets dans l'arbre :** `{list(etat.get('visites', []))}`")  # Ordre chronologique
                    st.metric("Coût total actuel", f"{etat.get('cout_total', 0):.0f} km")
                    st.metric("Arêtes dans l'arbre", f"{len(etat.get('arbre', []))} / {len(graphe)-1}")
                    
                    if etat.get("termine", False):
                        st.write("Arbre couvrant minimum terminé !")
                        st.session_state.en_cours = False
                        
                elif algo == "Kruskal":
                    if etat.get('arete_courante'):
                        u, v = etat['arete_courante']
                        st.markdown(f"**Arête examinée :** `{u} ↔ {v}`")
                    st.markdown(f"**Arêtes examinées :** `{etat.get('index_arete', 0)} / {len(etat.get('aretes_triees', []))}`")
                    st.metric("Coût total actuel", f"{etat.get('cout_total', 0):.0f} km")
                    st.metric("Arêtes dans l'arbre", f"{len(etat.get('arbre', []))} / {len(graphe)-1}")
                    
                    if etat.get("termine", False):
                        st.write("Arbre couvrant minimum terminé !")
                        st.session_state.en_cours = False
                
                elif algo == "Dijkstra":
                    st.markdown(f"**Départ :** `{etat['depart']}`")
                    st.markdown(f"**Arrivée :** `{etat['arrivee']}`")
                    if etat['sommet_courant']:
                        st.markdown(f"**Sommet courant :** `{etat['sommet_courant']}`")
                    st.markdown(f"**Visités :** `{list(etat['visites'])}`")  # Ordre chronologique
                    
                    if etat["termine"] and etat["chemin_trouve"]:
                        st.write("Chemin optimal trouvé !")
                        st.markdown(f"**Chemin :** `{' → '.join(etat['chemin_trouve'])}`")
                        distance_finale = etat['distances'][etat['arrivee']]
                        st.metric("Distance totale", f"{distance_finale:.0f} km")
                        st.session_state.en_cours = False
                    elif etat["termine"]:
                        st.write("Aucun chemin trouvé !")
                        st.session_state.en_cours = False
            else:
                st.write("Veuillez lancer le programme.")
            
            # Affichage de l'historique
            if st.session_state.historique:
                with st.expander(f"Historique des étapes ({len(st.session_state.historique)} étapes)", expanded=False):
                    for info_etape in st.session_state.historique:
                        if algo in ["BFS", "DFS"]:
                            if "file" in info_etape:
                                st.markdown(f"""
                                **Étape {info_etape['etape']}**  
                                Sommet: `{info_etape['courant']}` | File: `{info_etape['file']}` | Visités: `{info_etape['visites']}`
                                """)
                            elif "pile" in info_etape:
                                st.markdown(f"""
                                **Étape {info_etape['etape']}**  
                                Sommet: `{info_etape['courant']}` | Pile: `{info_etape['pile']}` | Visités: `{info_etape['visites']}`
                                """)
                        elif algo == "Prim":
                            if info_etape.get('arete'):
                                u, v = info_etape['arete']
                                st.markdown(f"""
                                **Étape {info_etape['etape']}**  
                                Ajout: `{u} ↔ {v}` ({info_etape['poids']:.0f} km) → Coût total: {info_etape['cout_total']:.0f} km
                                """)
                        elif algo == "Kruskal":
                            u, v = info_etape['arete']
                            status = "Acceptée" if info_etape['accepte'] else "Rejetée (cycle)"
                            st.markdown(f"""
                            **Étape {info_etape['etape']}** {status}  
                            Arête: `{u} ↔ {v}` ({info_etape['poids']:.0f} km) → Coût total: {info_etape['cout_total']:.0f} km
                            """)
                        elif algo == "Dijkstra":
                            st.markdown(f"""
                            **Étape {info_etape['etape']}**  
                            Sommet: `{info_etape['sommet']}` | Distance: {info_etape['distance']:.0f} km
                            """)
                        st.divider()
    
    # Boucle d'animation
    if categorie not in ["Ordonnancement PERT"]:
        # Floyd-Warshall n'a pas d'animation automatique
        if algo != "Floyd-Warshall":
            if st.session_state.en_cours and st.session_state.etat_algorithme and not st.session_state.etat_algorithme["termine"]:
                # Vérification de cohérence
                if algo == "BFS" and "file" not in st.session_state.etat_algorithme:
                    reinitialiser_animation()
                    st.rerun()
                elif algo == "DFS" and "pile" not in st.session_state.etat_algorithme:
                    reinitialiser_animation()
                    st.rerun()
                elif algo == "Prim" and "file_priorite" not in st.session_state.etat_algorithme:
                    reinitialiser_animation()
                    st.rerun()
                elif algo == "Kruskal" and "uf" not in st.session_state.etat_algorithme:
                    reinitialiser_animation()
                    st.rerun()
                elif algo == "Dijkstra" and "depart" not in st.session_state.etat_algorithme:
                    reinitialiser_animation()
                    st.rerun()
                elif algo == "Bellman-Ford" and "aretes" not in st.session_state.etat_algorithme:
                    reinitialiser_animation()
                    st.rerun()
                
                # Exécution de l'étape
                if algo == "BFS":
                    st.session_state.etat_algorithme = etape_bfs(graphe, st.session_state.etat_algorithme, st.session_state)
                elif algo == "DFS":
                    st.session_state.etat_algorithme = etape_dfs(graphe, st.session_state.etat_algorithme, st.session_state)
                elif algo == "Prim":
                    st.session_state.etat_algorithme = etape_prim(graphe, st.session_state.etat_algorithme, st.session_state)
                elif algo == "Kruskal":
                    st.session_state.etat_algorithme = etape_kruskal(graphe, st.session_state.etat_algorithme, st.session_state)
                elif algo == "Dijkstra":
                    st.session_state.etat_algorithme = etape_dijkstra(graphe, st.session_state.etat_algorithme, st.session_state)
                elif algo == "Bellman-Ford":
                    st.session_state.etat_algorithme = etape_bellman_ford(graphe, st.session_state.etat_algorithme, st.session_state)
                
                st.session_state.compteur_etapes += 1
                
                time.sleep(vitesse / 1000)
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Projet : Algorithmes de graphes</strong></p>
        <p>Un projet réalisé par William WAN & Hsiao-Wen-Paul LO</p>
    </div>
    """, unsafe_allow_html=True)