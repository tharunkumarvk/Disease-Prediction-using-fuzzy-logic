# fuzzy_app/cnn_model.py
import numpy as np
import os
from django.conf import settings
from tensorflow.keras.models import load_model
import pickle

class CNNModel:
    def __init__(self, model_path=os.path.join(settings.BASE_DIR, 'cnn_disease_model.h5'), 
                 encoder_path=os.path.join(settings.BASE_DIR, 'label_encoder.pkl')):
        # Load the pretrained model
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please place cnn_disease_model.h5 in the project root or update the path.")
        self.model = load_model(model_path)
        # Load the label encoder
        with open(encoder_path, 'rb') as f:
            self.le = pickle.load(f)
        self.reverse_mapping = {i: label for i, label in enumerate(self.le.classes_)}
        # Hardcoded descriptions based on init_db
        self.descriptions = {
            'Common Cold': 'Viral infection of the upper respiratory tract',
            'Flu': 'Influenza viral infection affecting the respiratory system',
            'Malaria': 'Mosquito-borne infectious disease causing fever and chills',
            'Dengue': 'Mosquito-borne tropical disease causing high fever'
        }

    def preprocess_input(self, symptom_values):
        input_data = np.array(symptom_values)
        # Normalize to 0-1 as per MinMaxScaler used in training
        input_data = (input_data - np.array([95, 0, 0, 0, 0])) / np.array([10, 10, 10, 10, 10])
        return input_data.reshape(1, 5, 1)

    def predict(self, symptom_values):
        input_data = self.preprocess_input(symptom_values)
        prediction = self.model.predict(input_data)
        disease_idx = np.argmax(prediction)
        confidence = prediction[0][disease_idx]
        disease_name = self.reverse_mapping[disease_idx]
        description = self.descriptions.get(disease_name, f"Description for {disease_name}")
        return {
            disease_name: {
                'confidence': round(float(confidence) * 100, 2),
                'description': description
            }
        }