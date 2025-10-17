from datetime import datetime, timezone

from pynamodb.attributes import (UnicodeAttribute,
                                 UTCDateTimeAttribute,
                                 MapAttribute)
# from ih_search_service.model.unicode_enum_attribute import UnicodeEnumAttribute

# from ih_search_service.enums.platform import Platform

from model.unicode_enum_attribute import UnicodeEnumAttribute
from enums.platform import Platform


class InfluencerPlatform(MapAttribute):
    influencer_id = UnicodeAttribute()
    platform = UnicodeEnumAttribute(Platform)
    influencer_handle = UnicodeAttribute()
    profile_url = UnicodeAttribute()
    profile_img_url = UnicodeAttribute()
    influencer_bio = UnicodeAttribute()
    influencer_email = UnicodeAttribute()
    profile_timestamp = UTCDateTimeAttribute(
        default=datetime.now(timezone.utc))
    created_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "influencer_id": self.influencer_id,
            "platform": self.platform.value,  # Convert Enum to string
            "influencer_handle": self.influencer_handle,
            "profile_url": self.profile_url,
            "profile_img_url": self.profile_img_url,
            "influencer_bio": self.influencer_bio,
            "influencer_email": self.influencer_email,
            "profile_timestamp": self.profile_timestamp.isoformat(),
            "created_at": self.created_at.isoformat() if self.created_at else 'N/A',
            "updated_at": self.updated_at.isoformat() if self.updated_at else 'N/A',
        }
