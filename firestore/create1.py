import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "許允蓁",
  "mail": "s1100913@pu.edu.tw",
  "lab": 579
}

doc_ref = db.collection("靜宜資管2026a").document("tcyang")
doc_ref.set(doc)
