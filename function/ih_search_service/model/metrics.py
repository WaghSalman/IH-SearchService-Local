import logging
import os
from datetime import datetime, timezone

from pynamodb.attributes import (UnicodeAttribute,
                                 UTCDateTimeAttribute,
                                 NumberAttribute)
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from model.unicode_enum_attribute import UnicodeEnumAttribute
from enums.platform import Platform

REGION_KEY = 'AWS_REGION'
DEFAULT_REGION = 'us-west-2'
TABLE_NAME = 'MetricsTable'
LOCAL_DYNAMODB_ENDPOINT = 'http://localhost:8000'


class MetricsInfluencerIdIndex(GlobalSecondaryIndex):
    """
    Global Secondary Index for querying metrics by influencer ID.
    """
    class Meta:
        index_name = "influencer_id_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    influencer_id = UnicodeAttribute(hash_key=True)
    platform = UnicodeEnumAttribute(enum_type=Platform, range_key=True)


class MetricsFollowersIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "total_followers_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    platform = UnicodeEnumAttribute(enum_type=Platform, hash_key=True)
    total_followers = NumberAttribute(range_key=True)


class MetricsEngagementRateIndex(GlobalSecondaryIndex):
    """
    Global Secondary Index for querying metrics by engagement rate.
    """
    class Meta:
        index_name = "engagement_rate_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    platform = UnicodeEnumAttribute(enum_type=Platform, hash_key=True)
    engagement_rate = NumberAttribute(range_key=True)


class Metrics(Model):

    class Meta:
        table_name = TABLE_NAME
        region = os.environ.get(REGION_KEY, DEFAULT_REGION)
        # if 'DYNAMODB_LOCAL' in os.environ:
        host = LOCAL_DYNAMODB_ENDPOINT

    id = UnicodeAttribute(hash_key=True)
    influencer_id = UnicodeAttribute()
    platform = UnicodeEnumAttribute(Platform)
    total_followers = NumberAttribute(default=0)
    engagement_rate = NumberAttribute(default=0)
    total_likes = NumberAttribute(default=0)
    total_comments = NumberAttribute(default=0)
    total_shares = NumberAttribute(default=0)
    total_views = NumberAttribute(default=0)
    total_posts = NumberAttribute(default=0)
    # Human-readable / abbreviated string representations (e.g. "11.9M")
    total_followers_str = UnicodeAttribute(null=True, default='')
    total_likes_str = UnicodeAttribute(null=True, default='')
    total_comments_str = UnicodeAttribute(null=True, default='')
    total_shares_str = UnicodeAttribute(null=True, default='')
    total_views_str = UnicodeAttribute(null=True, default='')
    total_posts_str = UnicodeAttribute(null=True, default='')
    created_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))

    influencer_id_idx = MetricsInfluencerIdIndex()
    platform_followers_idx = MetricsFollowersIndex()
    platform_engagement_rate_idx = MetricsEngagementRateIndex()

    def to_dict(self):
        return {
            "id": self.id,
            "influencer_id": self.influencer_id,
            "platform": self.platform.value,  # Convert Enum to string
            "total_followers": self.total_followers,
            "total_followers_str": getattr(self, 'total_followers_str', ''),
            "engagement_rate": self.engagement_rate,
            "total_likes": self.total_likes,
            "total_likes_str": getattr(self, 'total_likes_str', ''),
            "total_comments": self.total_comments,
            "total_comments_str": getattr(self, 'total_comments_str', ''),
            "total_shares": self.total_shares,
            "total_shares_str": getattr(self, 'total_shares_str', ''),
            "total_views": self.total_views,
            "total_views_str": getattr(self, 'total_views_str', ''),
            "total_posts": self.total_posts,
            "total_posts_str": getattr(self, 'total_posts_str', ''),
            "created_at": self.created_at.isoformat() if self.created_at else 'N/A',
            "updated_at": self.updated_at.isoformat() if self.updated_at else 'N/A',
        }

    @staticmethod
    def search_by_influencer_id(influencer_id, platform=None):
        """
        Search for metrics by influencer ID and optionally filter by platform.
        :param influencer_id: The ID of the influencer to search for.
        :param platform: Platform enum value (optional). If provided, query the index; else, scan all.
        :return: A list of metrics matching the criteria.
        """
        try:
            if platform:
                # Convert string to Platform enum if necessary
                if isinstance(platform, str):
                    try:
                        platform = Platform(platform)
                    except ValueError:
                        raise ValueError(
                            "Invalid platform value. Must be a valid Platform enum string.")
                if not isinstance(platform, Platform):
                    raise ValueError(
                        "Invalid platform value. Must be an instance of Platform enum.")
                # Query the index with influencer_id as hash key and platform as range key
                query = Metrics.influencer_id_idx.query(
                    influencer_id,
                    MetricsInfluencerIdIndex.platform == platform
                )
                return list(query)
            else:
                # Scan all and filter in Python
                metrics = Metrics.scan(Metrics.influencer_id == influencer_id)
                return list(metrics)
        except Exception as e:
            logging.error(f"Error searching by influencer ID: {e}")
            return None

    @staticmethod
    def search_by_followers_count(min_followers=0, max_followers=None, platform=None):
        """
        Search for metrics by total followers count using the MetricsFollowersIndex.
        :param min_followers: Minimum number of followers (inclusive).
        :param max_followers: Maximum number of followers (inclusive), or None for no upper limit.
        :param platform: Platform enum value (optional). If provided, query the index; else, scan all.
        :return: A list of metrics matching the criteria.
        """
        try:
            if platform:
                # Convert string to Platform enum if necessary
                if isinstance(platform, str):
                    try:
                        platform = Platform(platform)
                    except ValueError:
                        raise ValueError(
                            "Invalid platform value. Must be a valid Platform enum string.")
                if not isinstance(platform, Platform):
                    raise ValueError(
                        "Invalid platform value. Must be an instance of Platform enum.")
                # Compose the range key condition
                if max_followers is not None:
                    range_condition = MetricsFollowersIndex.total_followers.between(
                        min_followers, max_followers)
                else:
                    range_condition = MetricsFollowersIndex.total_followers >= min_followers
                # Query the index with platform as hash key and range condition
                query = Metrics.platform_followers_idx.query(
                    platform,
                    range_condition
                )
                return list(query)
            else:
                # Scan all and filter in Python
                metrics = Metrics.scan()
                return [
                    m for m in metrics
                    if m.total_followers >= min_followers and
                    (max_followers is None or m.total_followers <= max_followers)
                ]
        except Exception as e:
            logging.error(f"Error searching by followers count: {e}")
            return None

    @staticmethod
    def search_by_engagement_rate(min_engagement_rate=0, max_engagement_rate=None, platform=None):
        """
        Search for metrics by engagement rate using a range.
        :param min_engagement_rate: Minimum engagement rate (inclusive).
        :param max_engagement_rate: Maximum engagement rate (inclusive), or None for no upper limit.
        :param platform: Platform enum value (optional). If provided, query the index; else, scan all.
        :return: A list of metrics matching the criteria.
        """
        try:
            if platform:
                if not isinstance(platform, Platform):
                    raise ValueError(
                        "Invalid platform value. Must be an instance of Platform enum.")
                # Compose the key condition on the range key (engagement_rate).
                # DynamoDB does not allow using a primary key attribute in the
                # filter expression; use a key condition (between or >=) instead.
                if max_engagement_rate is not None:
                    range_condition = MetricsEngagementRateIndex.engagement_rate.between(
                        min_engagement_rate, max_engagement_rate
                    )
                else:
                    range_condition = MetricsEngagementRateIndex.engagement_rate >= min_engagement_rate

                # Query the index with platform as hash key and the composed range condition
                query = Metrics.platform_engagement_rate_idx.query(
                    platform,
                    range_condition
                )
                return list(query)
            else:
                # Scan all and filter in Python
                metrics = Metrics.scan()
                return [
                    m for m in metrics
                    if m.engagement_rate >= min_engagement_rate and
                    (max_engagement_rate is None or m.engagement_rate <=
                     max_engagement_rate)
                ]
        except Exception as e:
            logging.error(f"Error searching by engagement rate: {e}")
            return None
