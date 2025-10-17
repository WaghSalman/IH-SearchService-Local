""" Import Modules """
from marshmallow import Schema, fields
from enums.platform import Platform


class InfluencerPlatformSchema(Schema):
    """ Influencer Platform Schema """
    influencer_id = fields.Str(required=False)
    platform = fields.Str(
        required=True, validate=lambda p: p in Platform.__members__)
    influencer_handle = fields.Str(required=True)
    profile_url = fields.Str(required=True)
    profile_img_url = fields.Str(required=True)
    influencer_bio = fields.Str(required=True)
    influencer_email = fields.Str(required=True)
    profile_timestamp = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
