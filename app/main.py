from flask import Flask, jsonify, request
from app.api.routers.health import health_bp
from app.api.routers.cars import bp as cars_bp
from app.api.routers.claims import bp as claims_bp
from app.api.routers.history import bp as history_bp
from app.api.routers.policies import bp as policies_bp

app = Flask(__name__)

app.register_blueprint(health_bp)
app.register_blueprint(cars_bp)
app.register_blueprint(claims_bp)
app.register_blueprint(history_bp)
app.register_blueprint(policies_bp)

stores=[
    {'name': 'api',
     'cars': [ 
         {
            "id":1,
            "vin":"WVWZZZ1JZXW000001",
            "make":"VW",
            "model":"Golf",
            "yearOfManufacture":2018,
            "owner":{
                "id":7,
                "name":"Alice",
                "email":"alice@example.com"
            },
            "policies": [{
                    "policyId": 1,
                    "startDate": "2023-01-01",
                    "endDate": "2024-01-01",
                    "provider": "Insurance Co A"
                }
            ],
            "claims": [
                {
                    "claimId": 1,
                    "claimDate": "2023-06-15",
                    "amount": 1500.00,
                    "description": "Rear-end collision"
                }
            ]

         },
         {
            "id":2,
            "vin":"WVWZZZ1JZXW000002",
            "make":"VW",
            "model":"Golf",
            "yearOfManufacture":2018,
            "owner":{
                "id":7,
                "name":"Alice",
                "email":"alice@example.com"
            }
         }
     ]}
]


if __name__ == '__main__':
    app.run(debug=True)