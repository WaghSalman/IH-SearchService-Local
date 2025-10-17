""" Import Moudles """
from marshmallow import Schema, fields
from enums.platform import Platform


class MetricsSchema(Schema):
    """ Metrics Schema """
    id = fields.Str(required=True)
    influencer_id = fields.Str(required=True)
    platform = fields.Str(
        required=True, validate=lambda p: p in Platform.__members__)
    total_followers = fields.Int(required=True)
    engagement_rate = fields.Float(required=True)
    total_likes = fields.Int(required=True)
    total_comments = fields.Int(required=True)
    total_shares = fields.Int(required=True)
    total_views = fields.Int(required=True)
    total_posts = fields.Int(required=True)
    total_followers_str = fields.Str(required=False, allow_none=True)
    total_likes_str = fields.Str(required=False, allow_none=True)
    total_comments_str = fields.Str(required=False, allow_none=True)
    total_shares_str = fields.Str(required=False, allow_none=True)
    total_views_str = fields.Str(required=False, allow_none=True)
    total_posts_str = fields.Str(required=False, allow_none=True)
