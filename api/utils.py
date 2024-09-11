from .constants import TOP_500_CITIES

def is_valid_city(city):
    return city.lower() in [c.lower() for c in TOP_500_CITIES]