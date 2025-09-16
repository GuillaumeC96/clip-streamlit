"""
Page de prédiction de catégorie de produits
Utilise l'API AWS pour la classification d'images et de texte
"""

import os
import streamlit as st
from PIL import Image
import json
import pandas as pd
import requests
import io
import numpy as np
import re
import ast
import plotly.express as px

# Importer le module d'accessibilité
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from accessibility_streamlit_cloud import init_accessibility_state, render_accessibility_sidebar, apply_accessibility_styles

# Configuration de la page
st.set_page_config(
    page_title="Prédiction - Classification de Produits",
    page_icon="🔮",
    layout="wide"
)

# Configuration de l'API AWS
API_BASE_URL = os.environ.get("API_BASE_URL", "http://16.171.235.240")

# Initialiser l'état d'accessibilité
init_accessibility_state()

# Configuration de la page
st.set_page_config(
    page_title="Prédiction de Catégorie",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 Prédiction de Catégorie")

# Afficher les options d'accessibilité dans la sidebar
render_accessibility_sidebar()

# Appliquer les styles d'accessibilité
apply_accessibility_styles()

st.markdown("---")

@st.cache_data
def load_default_test_product():
    """
    Charger le produit de test par défaut depuis le dataset
    
    Returns:
        dict: Informations du produit de test ou None si erreur
    """
    try:
        # Charger les données des produits
        df = pd.read_csv('produits_original.csv')
        
        # Produit de test par défaut (montre Escort)
        test_product_id = '1120bc768623572513df956172ffefeb'
        product = df[df['uniq_id'] == test_product_id]
        
        if not product.empty:
            product = product.iloc[0]
            image_filename = f"{test_product_id}.jpg"
            image_path = f"Images/{image_filename}"
            
            # Vérifier si l'image existe
            if os.path.exists(image_path):
                # Nettoyer la description (enlever les \n et \t)
                description = product['description'] if pd.notna(product['description']) else product['product_name']
                if description:
                    description = description.replace('\n', ' ').replace('\t', ' ').strip()
                    # Garder seulement les 2 premières phrases pour la lisibilité
                    sentences = description.split('. ')
                    if len(sentences) > 2:
                        description = '. '.join(sentences[:2]) + '.'
                
                # Nettoyer les spécifications (parser le format Ruby/JSON)
                specs = product['product_specifications'] if pd.notna(product['product_specifications']) else f"Prix: {product['retail_price']} INR"
                if specs and specs.startswith('{"product_specification"'):
                    try:
                        # Remplacer => par : pour convertir en JSON valide
                        json_specs = specs.replace('=>', ':')
                        specs_data = json.loads(json_specs)
                        if 'product_specification' in specs_data:
                            key_specs = []
                            for spec in specs_data['product_specification'][:5]:  # Limiter à 5 specs
                                if 'key' in spec and 'value' in spec:
                                    key_specs.append(f"{spec['key']}: {spec['value']}")
                            specs = '; '.join(key_specs) if key_specs else f"Prix: {product['retail_price']} INR"
                    except:
                        specs = f"Prix: {product['retail_price']} INR"
                
                return {
                    'name': product['product_name'],
                    'brand': product['brand'] if pd.notna(product['brand']) else 'Escort',
                    'description': description,
                    'specifications': specs,
                    'image_path': image_path,
                    'image_filename': image_filename
                }
            else:
                st.warning(f"⚠️ Image non trouvée: {image_path}")
                return None
        else:
            st.warning("⚠️ Produit de test non trouvé dans les données")
            return None
            
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du produit de test: {str(e)}")
        return None

def call_prediction_api(image_file, text_description):
    """Appelle l'API FastAPI pour la prédiction."""
    try:
        # Pour les objets Streamlit UploadedFile, utiliser getvalue()
        image_bytes = image_file.getvalue()
        
        files = {'image': (image_file.name, image_bytes, image_file.type)}
        data = {'text_description': text_description}
        
        response = requests.post(f"{API_BASE_URL}/predict", files=files, data=data, timeout=30)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP d'erreur
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'appel à l'API de prédiction: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement de l'image: {e}")
        return {"success": False, "error": str(e)}


# Charger le produit de test par défaut
default_product = load_default_test_product()

# Lancer automatiquement la prédiction sur le produit de test au premier chargement
if default_product and not st.session_state.get('auto_prediction_done', False):
    st.session_state['auto_prediction_done'] = True
    st.session_state['test_prediction_launched'] = True

# Interface de prédiction
st.subheader("📤 Upload de l'image")
uploaded_file = st.file_uploader(
    "Choisissez une image de produit",
    type=['png', 'jpg', 'jpeg'],
    help="Formats supportés : PNG, JPG, JPEG"
)

# Affichage de l'image
if uploaded_file is not None:
    # Afficher l'image uploadée
    image = Image.open(uploaded_file)
    st.image(image, caption="Image uploadée", width=400)
    
    # Informations sur l'image
    st.info(f"📏 Dimensions : {image.size[0]} x {image.size[1]} pixels")
elif default_product and st.session_state.get('test_prediction_launched', False):
    # Afficher l'image du produit de test
    image = Image.open(default_product['image_path'])
    st.image(image, caption="Produit de test", width=400)
    st.info(f"📏 Dimensions : {image.size[0]} x {image.size[1]} pixels")

# Informations du produit
st.subheader("📝 Informations du produit")

if default_product and st.session_state.get('test_prediction_launched', False):
    # Utiliser les données du produit de test
    product_name = st.text_input(
        "Nom du produit",
        value=default_product['name'],
        placeholder="Ex: iPhone 14 Pro"
    )
    
    brand = st.text_input(
        "Marque du produit",
        value=default_product['brand'],
        placeholder="Ex: Apple"
    )
    
    description = st.text_area(
        "Description du produit",
        value=default_product['description'],
        placeholder="Ex: Smartphone haut de gamme avec caméra professionnelle"
    )
    
    specifications = st.text_area(
        "Spécifications techniques",
        value=default_product['specifications'],
        placeholder="Ex: 6.1 pouces, 128GB, iOS 16"
    )
else:
    # Interface normale pour saisie manuelle
    product_name = st.text_input(
        "Nom du produit",
        placeholder="Ex: iPhone 14 Pro"
    )
    
    brand = st.text_input(
        "Marque du produit",
        placeholder="Ex: Apple"
    )
    
    description = st.text_area(
        "Description du produit",
        placeholder="Ex: Smartphone haut de gamme avec caméra professionnelle"
    )
    
    specifications = st.text_area(
        "Spécifications techniques",
        placeholder="Ex: 6.1 pouces, 128GB, iOS 16"
    )

# Bouton de prédiction
if st.button("🔮 Prédire la catégorie", type="primary"):
    # Déterminer quelle image utiliser
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image_file = uploaded_file
    elif default_product and st.session_state.get('test_prediction_launched', False):
        image = Image.open(default_product['image_path'])
        # Créer un objet file-like pour l'API
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        image_file = type('obj', (object,), {'name': default_product['image_filename'], 'getvalue': lambda self=None: img_byte_arr.getvalue(), 'type': 'image/jpeg'})()
    else:
        st.error("❌ Veuillez uploader une image avant de faire une prédiction")
        st.stop()
    
    # Préparer la description complète
    full_description = f"{product_name} {brand} {description} {specifications}".strip()
    
    # Nettoyer la description des textes génériques
    def clean_generic_text(text):
        """Supprime les textes génériques qui ne sont pas des descriptions de produits"""
        generic_patterns = [
            r'marque\s+non\s+spécifiée',
            r'brand\s+not\s+specified',
            r'non\s+spécifié',
            r'not\s+specified',
            r'non\s+disponible',
            r'not\s+available',
            r'à\s+définir',
            r'to\s+be\s+defined',
            r'non\s+renseigné',
            r'not\s+provided'
        ]
        
        cleaned_text = text
        for pattern in generic_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Nettoyer les espaces multiples
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        return cleaned_text
    
    full_description = clean_generic_text(full_description)
    
    with st.spinner("🔄 Analyse en cours..."):
        # Prédiction avec l'API AWS
        result = call_prediction_api(image_file, full_description)
        
        # Affichage des résultats
        if result.get('success', False) and 'predicted_category' in result:
            st.success("✅ Prédiction terminée !")
            
            # Affichage des résultats en quatre colonnes
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Marque",
                    brand if brand else "Non spécifiée"
                )
            
            with col2:
                st.metric(
                    "Catégorie prédite",
                    result['predicted_category']
                )
            
            with col3:
                confidence = result.get('confidence', 0.0)
                st.metric(
                    "Confiance",
                    f"{confidence:.2%}"
                )
            
            with col4:
                inference_time = result.get('inference_time', 0.0)
                st.metric(
                    "⏱️ Temps d'inférence",
                    f"{inference_time:.3f}s"
                )
            
            # Affichage détaillé des scores avec graphique Plotly
            if 'scores' in result:
                st.subheader("📊 Scores de confiance par catégorie")
                scores_df = pd.DataFrame(result['scores'])
                
                # Raccourcir les noms de catégories pour l'affichage
                def shorten_category_name(category):
                    """Raccourcit le nom de catégorie pour l'affichage"""
                    if ' >> ' in category:
                        # Prendre seulement la première partie avant le premier >>
                        return category.split(' >> ')[0]
                    elif len(category) > 30:
                        # Tronquer si trop long
                        return category[:27] + "..."
                    return category
                
                scores_df['category_short'] = scores_df['category'].apply(shorten_category_name)
                
                # Configuration des couleurs selon le mode d'accessibilité
                if st.session_state.accessibility.get('color_blind', False):
                    colors = px.colors.qualitative.Safe
                elif st.session_state.accessibility.get('high_contrast', False):
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                             '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
                else:
                    colors = px.colors.qualitative.Set3
                
                # Créer le graphique en barres horizontales avec Plotly
                fig = px.bar(
                    scores_df, 
                    x='score',
                    y='category_short', 
                    orientation='h',  # Barres horizontales
                    title="Scores de Prédiction par Catégorie",
                    color='score',
                    color_continuous_scale='viridis' if st.session_state.accessibility.get('color_blind', False) 
                    else 'plasma' if st.session_state.accessibility.get('high_contrast', False) 
                    else 'Blues',
                    text='score',
                    hover_data={'category': True, 'category_short': False}  # Afficher le nom complet au survol
                )
                
                # Configuration du layout pour l'accessibilité
                bg_color = '#000000' if st.session_state.accessibility.get('high_contrast', False) else '#FFFFFF'
                text_color = '#FFFFFF' if st.session_state.accessibility.get('high_contrast', False) else '#000000'
                
                fig.update_layout(
                    xaxis_title="Score de Confiance",
                    yaxis_title="Catégories",
                    plot_bgcolor=bg_color,
                    paper_bgcolor=bg_color,
                    font=dict(
                        size=14 if not st.session_state.accessibility.get('large_text', False) else 18, 
                        color=text_color
                    ),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=14 if not st.session_state.accessibility.get('large_text', False) else 16,
                        font_family="Arial, sans-serif",
                        font_color="black",
                        bordercolor="black"
                    ),
                    margin=dict(l=150, r=50, t=80, b=50),  # Marge gauche plus grande pour les noms de catégories
                    height=400  # Hauteur adaptée aux barres horizontales
                )
                
                # Configuration des axes pour les barres horizontales
                fig.update_xaxes(
                    tickfont=dict(
                        color=text_color, 
                        size=14 if not st.session_state.accessibility.get('large_text', False) else 16
                    ),
                    tickformat='.2%'  # Format en pourcentage sur l'axe X (scores)
                )
                fig.update_yaxes(
                    tickfont=dict(
                        color=text_color, 
                        size=14 if not st.session_state.accessibility.get('large_text', False) else 16
                    )
                )
                
                # Configuration du texte sur les barres horizontales
                fig.update_traces(
                    texttemplate='%{text:.1%}',
                    textposition='outside',
                    textfont=dict(
                        color=text_color,
                        size=12 if not st.session_state.accessibility.get('large_text', False) else 16
                    )
                )
                
                # Afficher le graphique
                st.plotly_chart(fig, use_container_width=True, aria_label="Graphique des scores de prédiction par catégorie")
                
                # Tableau des scores pour l'accessibilité
                st.write("**Tableau des scores :**")
                scores_display = scores_df.copy()
                scores_display['score'] = scores_display['score'].apply(lambda x: f"{x:.2%}")
                scores_display = scores_display.sort_values('score', ascending=False)
                st.dataframe(scores_display, use_container_width=True)
            
            # Affichage des mots-clés extraits par l'API
            if 'keywords' in result and result['keywords']:
                st.subheader("🔑 Mots-clés extraits")
                st.write(", ".join(result['keywords']))
                
        else:
            error_msg = result.get('error', 'Erreur inconnue')
            st.error(f"❌ Erreur lors de la prédiction: {error_msg}")
            
            # Messages d'aide spécifiques selon le type d'erreur
            if 'timeout' in error_msg.lower():
                st.warning("⏱️ **Problème de timeout détecté**")
                st.info("💡 **Solutions possibles :**")
                st.info("• L'API AWS n'est pas disponible ou ne répond pas")
                st.info("• Le service est surchargé ou en maintenance")
                st.info("• Vérifiez la configuration de l'API")
            elif '503' in error_msg or '502' in error_msg:
                st.warning("🚫 **Service API indisponible**")
                st.info("💡 **Solutions possibles :**")
                st.info("• Le service API est en maintenance ou surchargé")
                st.info("• L'instance AWS a des problèmes de ressources")
                st.info("• Contactez l'administrateur du service")
            else:
                st.info("💡 Vérifiez la configuration de l'API AWS.")

# Informations sur le modèle
st.markdown("---")
st.success("✅ Système de prédiction API AWS initialisé")
st.info("💡 Prêt pour l'analyse d'images et la classification de produits")