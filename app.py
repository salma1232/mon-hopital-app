from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hopital_db"]
patients_collection = db["patients"]

# Page d'accueil - Liste des patients
@app.route('/')
def index():
    patients = patients_collection.find()
    return render_template('index.html', patients=patients)

# Ajouter un patient
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        antecedents_str = request.form['antecedents']
        antecedents_list = [a.strip() for a in antecedents_str.split(',') if a.strip()]

        patient = {
            "nom": request.form['nom'],
            "prenom": request.form['prenom'],
            "age": int(request.form['age']),
            "sexe": request.form['sexe'],
            "antecedents": antecedents_list,
            "consultations": []
        }
        patients_collection.insert_one(patient)
        return redirect(url_for('index'))
    return render_template('add_patient.html')

# Voir dossier d'un patient
@app.route('/patient/<patient_id>')
def view_patient(patient_id):
    patient = patients_collection.find_one({"_id": ObjectId(patient_id)})
    return render_template('view_patients.html', patient=patient)

# Ajouter une consultation
@app.route('/patient/<patient_id>/add_consultation', methods=['GET', 'POST'])
def add_consultation(patient_id):
    if request.method == 'POST':
        symptomes_str = request.form['symptomes']
        symptomes_list = [s.strip() for s in symptomes_str.split(',') if s.strip()]

        consultation = {
            "date": request.form['date'],
            "symptomes": symptomes_list,
            "diagnostic": request.form['diagnostic'],
            "prescriptions": [
                {
                    "medicament": request.form['medicament'],
                    "dose": request.form['dose'],
                    "duree": request.form['duree']
                }
            ],
            "examens": [
                {
                    "type": request.form['type_examen'],
                    "resultat": request.form['resultat_examen'],
                    "date": request.form['date_examen']
                }
            ]
        }

        patients_collection.update_one(
            {"_id": ObjectId(patient_id)},
            {"$push": {"consultations": consultation}}
        )
        return redirect(url_for('view_patient', patient_id=patient_id))
    return render_template('add_consultation.html', patient_id=patient_id)

# Supprimer un patient
@app.route('/delete/<patient_id>', methods=['GET'])
def delete_patient(patient_id):
    patients_collection.delete_one({"_id": ObjectId(patient_id)})
    return redirect(url_for('index'))

# Recherche flexible
@app.route('/search', methods=['GET'])
def search():
    query = {}

    symptome = request.args.get('symptome')
    diagnostic = request.args.get('diagnostic')
    traitement = request.args.get('traitement')

    if symptome:
        query["consultations.symptomes"] = symptome
    if diagnostic:
        query["consultations.diagnostic"] = diagnostic
    if traitement:
        query["consultations.prescriptions.medicament"] = traitement

    results = patients_collection.find(query)
    return render_template('index.html', patients=results)

if __name__ == '__main__':
    app.run(debug=True)

        
