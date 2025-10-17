""" Import Modules """
from marshmallow import Schema, fields, validate
from ih_search_service.enums.category import Category
from influencer_platform import InfluencerPlatformSchema
from metrics import MetricsSchema


class InfluencerSchema(Schema):
    """ Influencer Schema """
    id = fields.Str(required=False)
    name = fields.Str(required=True)
    location = fields.Str(required=True)
    gender = fields.Str(required=False)
    # category = fields.List(
    #     fields.Enum(enum=Category),
    #     required=True,
    #     validate=validate.ContainsOnly([category.value for category in Category]),
    # )
    category = fields.Str(Category, required=True)
    platforms = fields.List(fields.Nested(
        InfluencerPlatformSchema), required=True)
    metrics = fields.List(fields.Nested(MetricsSchema), required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
