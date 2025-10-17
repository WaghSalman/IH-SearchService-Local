from datetime import datetime, timezone
import logging
import os
import uuid

from pynamodb.models import Model
from pynamodb.attributes import (UnicodeAttribute,
                                 UTCDateTimeAttribute,
                                 NumberAttribute)
from model.unicode_enum_attribute import UnicodeEnumAttribute
from enums.platform import Platform

from pynamodb.exceptions import PutError
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex


REGION_KEY = 'AWS_REGION'
DEFAULT_REGION = 'us-west-2'
TABLE_NAME = 'PostTable'
LOCAL_DYNAMODB_ENDPOINT = 'http://localhost:8000'


class InfluencerIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_id_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    influencer_id = UnicodeAttribute(hash_key=True)


class PostIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "post_id_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    post_id = UnicodeAttribute(hash_key=True)


class PostUrlIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "post_url_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    url = UnicodeAttribute(hash_key=True)


class PostPlatformIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "post_platform_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    platform = UnicodeEnumAttribute(Platform, hash_key=True)


class Post(Model):
    class Meta:
        table_name = TABLE_NAME
        region = os.environ.get(REGION_KEY, DEFAULT_REGION)
        # if 'DYNAMODB_LOCAL' in os.environ:
        host = LOCAL_DYNAMODB_ENDPOINT

    post_id = UnicodeAttribute(hash_key=True)
    influencer_id = UnicodeAttribute()
    platform = UnicodeEnumAttribute(Platform)
    title = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(null=True)
    # original post timestamp
    post_created_at = UTCDateTimeAttribute(null=True)
    # post type (video, image, etc.)
    post_type = UnicodeAttribute(null=True)
    url = UnicodeAttribute()
    likes = NumberAttribute(null=True)
    likes_str = UnicodeAttribute(null=True)
    comments = NumberAttribute(null=True)
    comments_str = UnicodeAttribute(null=True)
    shares = NumberAttribute(null=True)
    shares_str = UnicodeAttribute(null=True)
    views = NumberAttribute(null=True)
    views_str = UnicodeAttribute(null=True)
    description = UnicodeAttribute(null=True)

    post_id_index = PostIdIndex()
    influencer_id_index = InfluencerIdIndex()
    post_url_index = PostUrlIndex()
    post_platform_index = PostPlatformIndex()

    def save_post(self):
        """Save a new post with a unique ID and current timestamps."""
        try:
            if not getattr(self, 'post_id', None):
                self.post_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            self.created_at = now
            self.updated_at = now
            self.save()
        except PutError as e:
            logging.error(f"Error saving post: {e}")
            raise

    @classmethod
    def get_post_by_id(cls, post_id):
        """Get a single post by its ID using the post_id_index."""
        try:
            result = list(cls.post_id_index.query(post_id))
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Error retrieving post with ID {post_id}: {e}")
            return None

    @classmethod
    def get_posts_by_influencer_id(cls, influencer_id, limit=None, exclusive_start_key=None):
        """Get all posts for a given influencer ID. Supports optional DB pagination."""
        try:
            # Use Model.query with index_name so that exclusive_start_key is
            # accepted consistently across PynamoDB versions.
            iterator = cls.query(
                influencer_id,
                index_name='influencer_id_index',
                limit=limit or None,
                last_evaluated_key=exclusive_start_key,
            )
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error retrieving posts for influencer ID {influencer_id}: {e}")
            return []

    @classmethod
    def get_posts_by_url(cls, url, limit=None, exclusive_start_key=None):
        """Get all posts for a given URL. Supports optional DB pagination."""
        try:
            iterator = cls.query(
                url,
                index_name='post_url_index',
                limit=limit or None,
                last_evaluated_key=exclusive_start_key,
            )
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error retrieving posts with URL {url}: {e}")
            return []

    @classmethod
    def get_posts_by_platform(cls, platform, limit=None, exclusive_start_key=None):
        """Get all posts for a given platform. 
        Supports optional DB pagination."""
        try:
            iterator = cls.query(
                platform,
                index_name='post_platform_index',
                limit=limit or None,
                last_evaluated_key=exclusive_start_key,
            )
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error retrieving posts for platform {platform}: {e}")
            return []

    @classmethod
    def get_all_posts(cls, limit=None, exclusive_start_key=None):
        """Scan and return all posts. Supports optional DB pagination."""
        try:
            iterator = cls.scan(limit=limit or None, last_evaluated_key=exclusive_start_key)
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error retrieving all posts: {e}")
            return []
