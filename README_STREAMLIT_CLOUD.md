# 🚀 Déploiement sur Streamlit Community Cloud

## 📋 Prérequis

- ✅ Repository GitHub : `clip-streamlit`
- ✅ API AWS déployée et accessible
- ✅ Compte Streamlit Community Cloud

## 🔧 Configuration

### 1. Configuration des secrets

Streamlit Cloud utilise le fichier `.streamlit/secrets.toml` pour la configuration.

Le fichier est déjà configuré avec :
```toml
[api]
base_url = "http://16.171.235.240"
timeout = 30
max_retries = 3
```

### 2. Personnalisation (optionnel)

Vous pouvez modifier le fichier `.streamlit/secrets.toml` pour personnaliser :

```toml
[api]
base_url = "http://16.171.235.240"  # URL de votre API
timeout = 30                        # Timeout en secondes
max_retries = 3                     # Nombre de tentatives

[app]
title = "Classification de Produits CLIP"
description = "Application de classification de produits utilisant CLIP et Streamlit"
version = "1.0.0"
```

## 🚀 Déploiement

### 1. Connecter le repository

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur "New app"
3. Sélectionnez le repository : `GuillaumeC96/clip-streamlit`
4. Branche : `main`
5. Fichier principal : `app.py` (détecté automatiquement)

### 2. Configuration avancée

- **Python version** : 3.10 (détecté automatiquement)
- **Dependencies** : `requirements.txt` (détecté automatiquement)
- **Secrets** : Configurés dans `.streamlit/secrets.toml`

## ✅ Vérification

### 1. Test de l'application

- ✅ Page d'accueil se charge
- ✅ Options d'accessibilité fonctionnent
- ✅ Page EDA affiche les données
- ✅ Page de prédiction se connecte à l'API

### 2. Test de l'API

```bash
# Test de connectivité
curl http://16.171.235.240/health

# Test de prédiction
curl -X POST http://16.171.235.240/predict \
  -F "image=@test_image.jpg" \
  -F "text=test product"
```

## 🔍 Dépannage

### Problèmes courants

1. **API non accessible** :
   - Vérifiez l'IP de l'instance AWS
   - Vérifiez les règles de sécurité (Security Groups)
   - Testez la connectivité depuis votre machine

2. **Erreurs de dépendances** :
   - Vérifiez `requirements.txt`
   - Vérifiez la version Python (3.10)

3. **Secrets non trouvés** :
   - L'application utilise des valeurs par défaut
   - Vérifiez que le fichier `.streamlit/secrets.toml` est présent

## 📊 Monitoring

- **Logs Streamlit** : Disponibles dans l'interface Streamlit Cloud
- **Logs API** : Disponibles sur l'instance AWS
- **Métriques** : Utilisation et performance dans Streamlit Cloud

## 🔄 Mise à jour

Pour mettre à jour l'application :

1. **Push sur GitHub** : Les changements se déploient automatiquement
2. **Secrets** : Mettez à jour le fichier `.streamlit/secrets.toml`
3. **Push** : Les changements se déploient automatiquement

## 📞 Support

- **Documentation Streamlit** : [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community** : [discuss.streamlit.io](https://discuss.streamlit.io)
- **Issues GitHub** : [github.com/GuillaumeC96/clip-streamlit/issues](https://github.com/GuillaumeC96/clip-streamlit/issues)
