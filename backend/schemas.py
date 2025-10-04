from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    name = fields.Str()
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class DatasetSchema(Schema):
    id = fields.Int(dump_only=True)
    filename = fields.Str(required=True)
    size_bytes = fields.Int()
    rows = fields.Int()
    cols = fields.Int()
    created_at = fields.DateTime(dump_only=True)

class AnalysisSchema(Schema):
    id = fields.Int(dump_only=True)
    dataset_id = fields.Int(required=True)
    mode = fields.Str()
    status = fields.Str()
    params = fields.Dict()
    metrics = fields.Dict()
    created_at = fields.DateTime(dump_only=True)