from datetime import datetime, timezone
import logging
import os

from pynamodb.models import Model
from pynamodb.attributes import (UnicodeAttribute,
                                 UTCDateTimeAttribute,
                                 ListAttribute)

from model.unicode_enum_attribute import UnicodeEnumAttribute
from enums.category import Category
from enums.gender import Gender
from enums.platform import Platform
from model.influencer_platform import InfluencerPlatform

from pynamodb.indexes import AllProjection, GlobalSecondaryIndex


REGION_KEY = 'AWS_REGION'
DEFAULT_REGION = 'us-west-2'
TABLE_NAME = 'InfluencerTable'
LOCAL_DYNAMODB_ENDPOINT = 'http://localhost:8000'


class InfluencerIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_id_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    influencer_id = UnicodeAttribute(hash_key=True)


class InfluencerNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_name_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    name = UnicodeAttribute(hash_key=True)


class InfluencerLocationIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_location_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    location = UnicodeAttribute(hash_key=True)


class InfluencerCategoryIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_category_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    # Keep the model-side attribute name different to avoid declaring a
    # hash key named `category` on the model class (which would collide
    # with the primary key). Map to the DynamoDB attribute name 'category'.
    category_index = UnicodeEnumAttribute(Category, hash_key=True, attr_name='category')

class InfluencerGenderIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_gender_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    gender = UnicodeEnumAttribute(Gender, hash_key=True)


class InfluencerPlatformIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "influencer_platform_index"
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()

    # Updated to use UnicodeEnumAttribute with Platform enum
    platform = UnicodeEnumAttribute(Platform, hash_key=True)


class Influencer(Model):
    class Meta:
        table_name = TABLE_NAME
        region = os.environ.get(REGION_KEY, DEFAULT_REGION)
        # if 'DYNAMODB_LOCAL' in os.environ:
        host = LOCAL_DYNAMODB_ENDPOINT

    influencer_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    location = UnicodeAttribute()
    gender = UnicodeEnumAttribute(Gender)
    # Store a single category as an enum-backed string attribute
    category = UnicodeEnumAttribute(Category)
    platforms = ListAttribute(of=InfluencerPlatform)
    created_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))

    influencer_id_index = InfluencerIdIndex()
    influencer_name_index = InfluencerNameIndex()
    influencer_location_index = InfluencerLocationIndex()
    influencer_gender_index = InfluencerGenderIndex()
    influencer_platform_index = InfluencerPlatformIndex()
    influencer_category_index = InfluencerCategoryIndex()

    def to_dict(self):
        return {
            "influencer_id": self.influencer_id,
            "name": self.name,
            "location": self.location,
            "gender": self.gender,
            "category": self.category.value if self.category else 'N/A',
            "platforms": [platform.to_dict() for platform in self.platforms] if self.platforms else [],
            "created_at": self.created_at.isoformat() if self.created_at else 'N/A',
            "updated_at": self.updated_at.isoformat() if self.updated_at else 'N/A',
        }

    @staticmethod
    def search_by_id(influencer_id):
        """
        Search for an influencer by their ID.
        """
        try:
            iterator = Influencer.influencer_id_index.query(influencer_id)
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error searching by ID: {e}")
            return [], None

    @staticmethod
    def search_by_name(name, limit=None, exclusive_start_key=None):
        """
        Search for influencers by their name.
        """
        try:
            filter_condition = Influencer.name.contains(name)
            # PynamoDB scan supports limit and exclusive_start_key
            iterator = Influencer.scan(filter_condition, limit=limit or None, exclusive_start_key=exclusive_start_key)
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error searching by name: {e}")
            return None

    @staticmethod
    def search_by_location(location, limit=None, exclusive_start_key=None):
        """
        Search for influencers by their location.
        """
        try:
            iterator = Influencer.influencer_location_index.query(location, 
                        limit=limit or None, exclusive_start_key=exclusive_start_key)
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error searching by location: {e}")
            return None

    @staticmethod
    def search_by_gender(gender, limit=None, exclusive_start_key=None):
        """
        Search influencers by their gender
        """
        try:
            if not isinstance(gender, Gender):
                raise ValueError(
                    "Invalid gender value. "
                    "Must be an instance of Gender enum."
                )
            iterator = Influencer.influencer_gender_index.query(
                gender,
                limit=limit or None,
                exclusive_start_key=exclusive_start_key,
            )
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error searching by gender: {e}")
            return None

    @staticmethod
    def search_by_category(category_values, limit=None, exclusive_start_key=None):
        """
        Search influencers by category values (list of strings or single string).
        Returns influencers that have any of the provided category values.
        """
        try:
            # Normalize to list of strings
            if category_values is None:
                return None
            if isinstance(category_values, str):
                values = [category_values]
            else:
                values = list(category_values)

            # For category we still need to scan and filter in-memory; support limit via simple slicing
            all_influencers = list(Influencer.scan())
            filtered = [inf for inf in all_influencers if any(c in (inf.category or []) for c in values)]
            return filtered, None
        except Exception as e:
            logging.error(f"Error searching by category: {e}")
            return None

    @staticmethod
    def search_by_platform(platform, limit=None, exclusive_start_key=None):
        """
        Search for influencers by their platform.
        :param platform: The platform to filter by (e.g., Platform.INSTAGRAM).
        :return: A list of influencers matching the platform.
        """
        try:
            if not isinstance(platform, Platform):
                raise ValueError(
                    "Invalid platform value. Must be an instance of Platform enum.")
            # Platforms are stored in a list attribute; fall back to scanning
            iterator = Influencer.scan(limit=limit or None, exclusive_start_key=exclusive_start_key)
            # Controller will filter and inspect iterator.last_evaluated_key
            last_key = getattr(iterator, 'last_evaluated_key', None)
            return iterator, last_key
        except Exception as e:
            logging.error(f"Error searching by platform: {e}")
            return None
