""" Import Modules """
from enum import Enum


class Gender(str, Enum):
    """ Gender Enum """
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'
