
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models.bank_account import BankAccount
from alveare.views.bank_account import serializer, deserializer, update_deserializer
from alveare.common.database import DB


class BankAccountCollection(Resource):

    def get(self):
        bank_accounts = BankAccount.query.all()
        response = jsonify(bank_accounts = serializer.dump(bank_accounts, many=True).data)
        return response

    def post(self):
        new_account = deserializer.load(request.form or request.json).data

        DB.session.add(new_account)
        DB.session.commit()

        response = jsonify(bank_account=serializer.dump(new_account).data)
        response.status_code = 201
        return response


class BankAccountResource(Resource):

    def get(self, id):
        account = BankAccount.query.get_or_404(id)
        return jsonify(bank_account = serializer.dump(account).data)

    def put(self, id):
        updated_account = update_deserializer.load(request.form or request.json).data

        DB.session.add(updated_account)
        DB.session.commit()

        response = jsonify(organization=serializer.dump(updated_account).data)
        response.status_code = 200
        return response

    def delete(self, id):
        DB.session.query(BankAccount).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'BankAccount succesfully deleted')
        response.status_code = 200
        return response
