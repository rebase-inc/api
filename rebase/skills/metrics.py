from collections import defaultdict

from .tech_profile import TechProfile
from .tech_profile_view import TechProfileView


def measure(tech_profile):
    '''

    Returns an object:

    {
        '_overall': score,

        'Python': score,
        'Python.__language__': score,
        'Python.__standard_library__': score,
        'Python.__third_party__': score,
        'Python.__third_party__.boto3': score,

        'Javascript': score,
        'Javascript.__language__': score,
        'Javascript.__standard_library__': score,
        'Javascript.__third_party__': score,
        'Javascript.__third_party__.react': score,
        ...
    }

    'score' is the 'experience' as defined in TechProfileView.experience

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

        # 2nd level ('__language__', '__standard_library__', '__third_party__')
        three_level_profiles['.'.join(levels[:2])][tech] = exposure

        if levels[1] == '__third_party__':
            three_level_profiles['.'.join(levels[:3])][tech] = exposure

    for level, profile in three_level_profiles.items():
        metrics[level] = TechProfileView(profile).experience
    return metrics


