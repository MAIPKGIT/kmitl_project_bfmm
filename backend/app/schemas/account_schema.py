from marshmallow import Schema, fields

class AccountSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    mail = fields.Str()
    phone = fields.Str()
    role = fields.Str()
    create = fields.DateTime(dump_only=True)
