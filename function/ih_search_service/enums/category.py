""" Import Modules """
from enum import Enum


class Category(str, Enum):
    """ Category Enum """
    FITNESS = "FITNESS"
    FASHION = "FASHION"
    TRAVEL = "TRAVEL"
    BEAUTY = "BEAUTY"
    LIFESTYLE = "LIFESTYLE"
    FOOD = "FOOD"
    TECH = "TECH"
    GAMING = "GAMING"
    POLITICS = "POLITICS"
    MUSIC = "MUSIC"
    ATHLETES = "ATHLETES"
    COMEDY = "COMEDY"
