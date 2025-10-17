from marshmallow import Schema, fields
from enums.platform import Platform


class PostSchema(Schema):
    post_id = fields.Str(dump_only=True)
    influencer_id = fields.Str(required=True)
    platform = fields.Str(required=True, validate=lambda p: p in Platform.__members__)
    title = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(allow_none=True)
    post_created_at = fields.DateTime(allow_none=True)
    post_type = fields.Str(allow_none=True)
    url = fields.Str(required=True)
    likes = fields.Int(allow_none=True)
    likes_str = fields.Str(allow_none=True)
    comments = fields.Int(allow_none=True)
    comments_str = fields.Str(allow_none=True)
    shares = fields.Int(allow_none=True)
    shares_str = fields.Str(allow_none=True)
    views = fields.Int(allow_none=True)
    views_str = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
