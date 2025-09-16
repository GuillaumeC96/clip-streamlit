"""
Application Streamlit Cloud - Classification de Produits
Point d'entrée principal pour le déploiement sur Streamlit Cloud
"""

import streamlit as st
import accessibility_streamlit_cloud as accessibility

# Configuration de la page
st.set_page_config(
    page_title="Classification de Produits",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser les options d'accessibilité
accessibility.init_accessibility_state()

# Titre principal
st.markdown("""
# 🔮 Application de Classification de Produits

Bienvenue dans l'application de classification de produits utilisant l'API AWS !
""")

# Options d'accessibilité
accessibility.render_accessibility_sidebar()

# Appliquer les styles d'accessibilité
accessibility.apply_accessibility_styles()

st.markdown("""
## 🚀 Fonctionnalités

- ✅ **Classification d'images** via API AWS
- ✅ **Prétraitement identique** au notebook de référence
- ✅ **Interface d'accessibilité** complète
- ✅ **Gestion robuste** des erreurs

## 📱 Navigation

Utilisez la sidebar pour naviguer entre les pages :
- **🔮 Prédiction** : Classification de produits
- **📊 EDA** : Analyse exploratoire des données

---

**🎯 Application prête pour la classification de produits !**
""")

# Lien vers la page de prédiction
if st.button("🔮 Aller à la page de prédiction", type="primary"):
    st.switch_page("pages/2_prediction.py")