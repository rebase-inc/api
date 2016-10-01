from collections import defaultdict

from .tech_profile import TechProfile
from .tech_profile_view import TechProfileView


def measure(tech_profile):
    '''

    Returns an object:

    {
        'overall': score,
        'languages': {
                'Python': score,
                'Javascript': score,
        }
    }

    '''
    overall = TechProfileView(tech_profile).experience
    languages_profiles = defaultdict(TechProfile)
    languages = dict()
    for tech, exposure in tech_profile.items():
        languages_profiles[tech.split('.', maxsplit=1)[0]][tech] = exposure
    for language, profile in languages_profiles.items():
        languages[language] = TechProfileView(profile).experience
    return {
        'overall': overall,
        'languages': languages
    }


