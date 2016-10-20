from collections import defaultdict

from .tech_profile import TechProfile
from .tech_profile_view import TechProfileView


def measure(tech_profile):
    '''

    Returns an object:

    {
        '_overall': experience,

        'Python': experience,
        'Python.__language__': experience,
        'Python.__third_party__.boto3': experience,

        'Javascript': experience,
        'Javascript.__language__': experience,
        'Javascript.__third_party__.react': experience,
        ...
    }

    'experience' is the output of TechProfileView.experience for that key.

    The '__language__' level combines the '__grammar__' & '__standard_library__' levels from the TechProfile.

    '''
    metrics = {
        '_overall': TechProfileView(tech_profile).experience
    }
    three_level_profiles = defaultdict(TechProfile)
    languages = dict()
    for tech, exposure in tech_profile.items():
        levels = tech.split('.', maxsplit=3)
        # language level
        language = levels[0]
        three_level_profiles[language][tech] = exposure
        if levels[1] == '__3rd_party__':
            # this produces '__3rd_party__.sqlalchemy' type entries
            three_level_profiles['.'.join(levels[:3])][tech] = exposure
        else:
            # new combo level '__language__' aggregates entries from grammar & standard library
            three_level_profiles[language+'.__language__'][tech] = exposure

    for level, profile in three_level_profiles.items():
        metrics[level] = TechProfileView(profile).experience
    return metrics


