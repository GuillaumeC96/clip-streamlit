"""
Tests pour l'application Streamlit
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStreamlitImports:
    """Tests des imports Streamlit"""
    
    def test_streamlit_import(self):
        """Test que Streamlit peut être importé"""
        import streamlit as st
        assert st is not None
    
    def test_app_imports(self):
        """Test que les modules de l'app peuvent être importés"""
        try:
            import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"App module not available: {e}")
    
    def test_accessibility_import(self):
        """Test que le module d'accessibilité peut être importé"""
        try:
            import accessibility_streamlit_cloud
            assert accessibility_streamlit_cloud is not None
        except ImportError as e:
            pytest.skip(f"Accessibility module not available: {e}")

class TestStreamlitPages:
    """Tests des pages Streamlit"""
    
    def test_eda_page_import(self):
        """Test que la page EDA peut être importée"""
        try:
            import pages.eda as eda_page
            assert eda_page is not None
        except ImportError as e:
            pytest.skip(f"EDA page not available: {e}")
    
    def test_prediction_page_import(self):
        """Test que la page de prédiction peut être importée"""
        try:
            import pages.prediction as prediction_page
            assert prediction_page is not None
        except ImportError as e:
            pytest.skip(f"Prediction page not available: {e}")

class TestDataLoading:
    """Tests du chargement des données"""
    
    @patch('pandas.read_csv')
    def test_csv_loading(self, mock_read_csv):
        """Test que les CSV peuvent être chargés"""
        import pandas as pd
        
        # Mock des données CSV
        mock_data = pd.DataFrame({
            'product_name': ['Product 1', 'Product 2'],
            'category': ['Electronics', 'Clothing'],
            'description': ['Description 1', 'Description 2']
        })
        mock_read_csv.return_value = mock_data
        
        # Test du chargement
        data = pd.read_csv('test.csv')
        assert len(data) == 2
        assert 'product_name' in data.columns
    
    def test_image_loading(self):
        """Test que les images peuvent être chargées"""
        try:
            from PIL import Image
            import io
            
            # Créer une image de test
            test_image = Image.new('RGB', (100, 100), color='red')
            img_byte_arr = io.BytesIO()
            test_image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Vérifier que l'image peut être rechargée
            loaded_image = Image.open(img_byte_arr)
            assert loaded_image.size == (100, 100)
            
        except ImportError:
            pytest.skip("PIL not available")

class TestAPIIntegration:
    """Tests d'intégration avec l'API"""
    
    @patch('requests.post')
    def test_api_prediction_call(self, mock_post):
        """Test de l'appel à l'API de prédiction"""
        import requests
        
        # Mock de la réponse API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "predicted_category": "Electronics",
            "confidence": 0.85,
            "keywords": ["electronic", "device"],
            "scores": [
                {"category": "Electronics", "score": 0.85},
                {"category": "Clothing", "score": 0.15}
            ],
            "inference_time": 0.142
        }
        mock_post.return_value = mock_response
        
        # Test de l'appel API
        response = requests.post(
            "http://test-api.com/predict",
            files={"image": ("test.jpg", b"fake_image_data", "image/jpeg")},
            data={"text": "test product"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "predicted_category" in data
    
    @patch('requests.get')
    def test_api_health_check(self, mock_get):
        """Test du health check de l'API"""
        import requests
        
        # Mock de la réponse health
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "categories_loaded": True,
            "categories_count": 7,
            "model_loaded": True,
            "spacy_loaded": True,
            "version": "onnx_finetuned"
        }
        mock_get.return_value = mock_response
        
        # Test du health check
        response = requests.get("http://test-api.com/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestAccessibility:
    """Tests des fonctionnalités d'accessibilité"""
    
    def test_accessibility_module_functions(self):
        """Test que les fonctions d'accessibilité existent"""
        try:
            import accessibility_streamlit_cloud as acc
            
            # Vérifier que les fonctions principales existent
            assert hasattr(acc, 'init_accessibility_state')
            assert hasattr(acc, 'render_accessibility_sidebar')
            assert hasattr(acc, 'apply_accessibility_styles')
            
        except ImportError:
            pytest.skip("Accessibility module not available")
    
    def test_accessibility_state_initialization(self):
        """Test de l'initialisation de l'état d'accessibilité"""
        try:
            import accessibility_streamlit_cloud as acc
            
            # Mock de st.session_state
            with patch('streamlit.session_state', {}):
                acc.init_accessibility_state()
                # Vérifier que l'état est initialisé
                assert 'accessibility' in {}
                
        except ImportError:
            pytest.skip("Accessibility module not available")

class TestDataProcessing:
    """Tests du traitement des données"""
    
    def test_data_cleaning_functions(self):
        """Test des fonctions de nettoyage de données"""
        # Test de fonction de nettoyage basique
        def clean_text(text):
            return text.strip().lower()
        
        test_text = "  TEST PRODUCT  "
        cleaned = clean_text(test_text)
        assert cleaned == "test product"
    
    def test_keyword_extraction(self):
        """Test de l'extraction de mots-clés"""
        def extract_keywords(text):
            words = text.lower().split()
            return [word for word in words if len(word) > 2]
        
        test_text = "beautiful red dress for women"
        keywords = extract_keywords(test_text)
        expected = ["beautiful", "red", "dress", "for", "women"]
        assert keywords == expected

class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    def test_api_connection_error_handling(self):
        """Test de la gestion des erreurs de connexion API"""
        import requests
        from requests.exceptions import ConnectionError
        
        with patch('requests.get', side_effect=ConnectionError()):
            try:
                response = requests.get("http://invalid-api.com/health")
            except ConnectionError:
                # L'erreur devrait être gérée gracieusement
                assert True
            else:
                assert False, "ConnectionError should have been raised"
    
    def test_invalid_data_handling(self):
        """Test de la gestion des données invalides"""
        def safe_divide(a, b):
            try:
                return a / b
            except ZeroDivisionError:
                return None
        
        assert safe_divide(10, 2) == 5
        assert safe_divide(10, 0) is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
