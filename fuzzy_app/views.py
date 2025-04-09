from django.shortcuts import render, redirect
from .forms import SymptomInputForm
from .fuzzy_logic import FuzzySystem
from .models import Symptom, Disease, DiseaseRule
from .cnn_model import CNNModel

def index(request):
    if request.method == 'POST':
        form = SymptomInputForm(request.POST)
        if form.is_valid():
            # Prepare symptom values
            symptom_values = {}
            symptom_order = []  # To align with CNN input: [fever, headache, cough, fatigue, body_pain]
            for field_name, value in form.cleaned_data.items():
                if value is not None and field_name.startswith('symptom_'):
                    symptom_id = int(field_name.split('_')[1])
                    symptom = Symptom.objects.get(id=symptom_id)
                    symptom_name = symptom.name
                    symptom_values[symptom_name] = float(value)
                    # Map to CNN order
                    if symptom_name == 'Fever':
                        symptom_order.append(float(value))
                    elif symptom_name == 'Headache':
                        symptom_order.append(float(value))
                    elif symptom_name == 'Cough':
                        symptom_order.append(float(value))
                    elif symptom_name == 'Fatigue':
                        symptom_order.append(float(value))
                    elif symptom_name == 'Body Pain':
                        symptom_order.append(float(value))

            # Fuzzy prediction
            fuzzy_system = FuzzySystem()
            fuzzy_system.load_from_db()
            fuzzy_results = fuzzy_system.predict_disease(symptom_values)

            # CNN prediction with error handling
            try:
                cnn_model = CNNModel()
                cnn_results = cnn_model.predict(symptom_order)
            except Exception as e:
                cnn_results = {'Error': {'confidence': 0, 'description': f'CNN prediction failed: {str(e)}'}}

            # Combine results for consensus
            combined_results = {
                'fuzzy': fuzzy_results,
                'cnn': cnn_results
            }

            # Weighted consensus prediction
            consensus_result = {}
            if fuzzy_results and cnn_results and 'Error' not in cnn_results:
                fuzzy_disease = next(iter(fuzzy_results))
                cnn_disease = next(iter(cnn_results))
                fuzzy_conf = fuzzy_results[fuzzy_disease]['confidence'] / 100  # Convert to 0-1
                cnn_conf = cnn_results[cnn_disease]['confidence'] / 100  # Convert to 0-1
                # Simple weighting: 50% Fuzzy, 50% CNN (adjustable)
                total_conf = (0.5 * fuzzy_conf + 0.5 * cnn_conf) * 100
                # Choose the disease with higher individual confidence as the consensus
                consensus_disease = fuzzy_disease if fuzzy_conf >= cnn_conf else cnn_disease
                consensus_description = fuzzy_results.get(consensus_disease, {}).get('description', 
                                                                                  cnn_results.get(consensus_disease, {}).get('description', 
                                                                                  'No description available'))
                consensus_result = {
                    consensus_disease: {
                        'confidence': round(total_conf, 2),
                        'description': consensus_description
                    }
                }
            elif fuzzy_results:
                consensus_result = fuzzy_results
            elif cnn_results and 'Error' not in cnn_results:
                consensus_result = cnn_results
            else:
                consensus_result = {'Error': {'confidence': 0, 'description': 'No valid prediction'}}

            return render(request, 'fuzzy_app/results.html', {
                'results': combined_results,  # Individual Fuzzy and CNN results
                'consensus': consensus_result,  # Consensus result
                'symptom_values': symptom_values
            })
    else:
        form = SymptomInputForm()

    return render(request, 'fuzzy_app/index.html', {'form': form})

def about(request):
    return render(request, 'fuzzy_app/about.html')

def init_db(request):
    """Initialize database with sample data (for development)"""
    if not Symptom.objects.exists():
        # Create symptoms
        symptoms = [
            {'name': 'Fever', 'min_value': 95, 'max_value': 105, 'unit': '°F'},
            {'name': 'Headache', 'min_value': 0, 'max_value': 10, 'unit': 'scale'},
            {'name': 'Cough', 'min_value': 0, 'max_value': 10, 'unit': 'scale'},
            {'name': 'Fatigue', 'min_value': 0, 'max_value': 10, 'unit': 'scale'},
            {'name': 'Body Pain', 'min_value': 0, 'max_value': 10, 'unit': 'scale'},
        ]
        
        for symptom_data in symptoms:
            Symptom.objects.create(**symptom_data)
        
        # Create diseases
        diseases = [
            {'name': 'Common Cold', 'description': 'Viral infection of the upper respiratory tract'},
            {'name': 'Malaria', 'description': 'Mosquito-borne infectious disease causing fever and chills'},
            {'name': 'Cough', 'description': 'Condition characterized by persistent coughing'},
            {'name': 'Asthma', 'description': 'Chronic respiratory condition causing wheezing'},
            {'name': 'Normal Fever', 'description': 'Mild fever without specific cause'},
            {'name': 'Body Ache', 'description': 'Generalized body pain condition'},
            {'name': 'Runny Nose', 'description': 'Symptom of nasal congestion'},
            {'name': 'Dengue', 'description': 'Mosquito-borne tropical disease causing high fever'},
        ]
        
        disease_objs = {}
        for disease_data in diseases:
            disease_objs[disease_data['name']] = Disease.objects.create(**disease_data)
        
        # Create rules
        rules = [
            # Common Cold
            {'disease': 'Common Cold', 'symptom': 'Fever', 'severity': 'medium', 'weight': 0.7},
            {'disease': 'Common Cold', 'symptom': 'Headache', 'severity': 'medium', 'weight': 0.6},
            {'disease': 'Common Cold', 'symptom': 'Cough', 'severity': 'medium', 'weight': 0.8},
            {'disease': 'Common Cold', 'symptom': 'Fatigue', 'severity': 'medium', 'weight': 0.7},
            # Malaria
            {'disease': 'Malaria', 'symptom': 'Fever', 'severity': 'high', 'weight': 0.9},
            {'disease': 'Malaria', 'symptom': 'Headache', 'severity': 'medium', 'weight': 0.6},
            {'disease': 'Malaria', 'symptom': 'Fatigue', 'severity': 'high', 'weight': 0.8},
            {'disease': 'Malaria', 'symptom': 'Body Pain', 'severity': 'medium', 'weight': 0.5},
            # Cough
            {'disease': 'Cough', 'symptom': 'Cough', 'severity': 'high', 'weight': 0.9},
            {'disease': 'Cough', 'symptom': 'Fatigue', 'severity': 'medium', 'weight': 0.6},
            {'disease': 'Cough', 'symptom': 'Headache', 'severity': 'medium', 'weight': 0.5},
            # Asthma
            {'disease': 'Asthma', 'symptom': 'Cough', 'severity': 'medium', 'weight': 0.7},
            {'disease': 'Asthma', 'symptom': 'Fatigue', 'severity': 'medium', 'weight': 0.6},
            {'disease': 'Asthma', 'symptom': 'Headache', 'severity': 'low', 'weight': 0.4},
            # Normal Fever
            {'disease': 'Normal Fever', 'symptom': 'Fever', 'severity': 'medium', 'weight': 0.9},
            {'disease': 'Normal Fever', 'symptom': 'Headache', 'severity': 'medium', 'weight': 0.6},
            # Body Ache
            {'disease': 'Body Ache', 'symptom': 'Body Pain', 'severity': 'high', 'weight': 0.7},
            {'disease': 'Body Ache', 'symptom': 'Fatigue', 'severity': 'medium', 'weight': 0.6},
            {'disease': 'Body Ache', 'symptom': 'Headache', 'severity': 'medium', 'weight': 0.5},
            # Runny Nose
            {'disease': 'Runny Nose', 'symptom': 'Fever', 'severity': 'low', 'weight': 0.7},
            {'disease': 'Runny Nose', 'symptom': 'Headache', 'severity': 'low', 'weight': 0.6},
            # Dengue
            {'disease': 'Dengue', 'symptom': 'Fever', 'severity': 'high', 'weight': 0.9},
            {'disease': 'Dengue', 'symptom': 'Headache', 'severity': 'high', 'weight': 0.8},
            {'disease': 'Dengue', 'symptom': 'Fatigue', 'severity': 'high', 'weight': 0.8},
            {'disease': 'Dengue', 'symptom': 'Body Pain', 'severity': 'medium', 'weight': 0.7},
        ]
        
        for rule_data in rules:
            DiseaseRule.objects.create(
                disease=disease_objs[rule_data['disease']],
                symptom=Symptom.objects.get(name=rule_data['symptom']),
                severity=rule_data['severity'],
                weight=rule_data['weight']
            )
        
        return redirect('fuzzy_app:index')
    
    return redirect('fuzzy_app:index')