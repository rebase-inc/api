from builtins import super
from collections import defaultdict


class Exposure(object):

    def __init__(self, first=0, last=0, total_reps=0):
        self.first = first
        self.last = last
        self.total_reps = total_reps

    def add(self, date, reps):
        if (date < self.first) or (self.first == 0):
            self.first = date
        if date > self.last:
            self.last = date
        self.total_reps += reps

    def merge(self, exposure):
        if self.first == 0:
            self.first = exposure.first
        if self.last == 0:
            self.last = exposure.last
        if exposure.first < self.first:
            self.first = exposure.first
        if exposure.last > self.last:
            self.last = exposure.last
        self.total_reps += exposure.total_reps


class TechProfile(defaultdict):
    '''

    TechProfile gather metrics attempting to evaluate a developer's skill level.
    Obviously, this will always be somewhat incomplete, and not fool proof.
    But the goal here is to get a good enough correlation that we can weed out
    most bad candidates or find out which areas people shine in.

    We measure:

    - language skills by parsing the AST of the code for all the possible grammar constructs.
    - standard libraries knowledge (libraries managed with the language)
    - ecosystem technologies (public libraries stored on package managers: PyPI, NPM, etc.)
    - private technologies (the rest of libraries not the above two categories)

    We do not measure (yet?):

    Any contextual information about the nature of the problem being solved by the code (bioinformatics, rocketry, music, etc.)

    '''

    def __init__(self, *args, **kwargs):
        super().__init__(Exposure, *args, **kwargs)

    def __reduce__(self):
        ''' this allows pickle.dump/load to work. '''
        return (TechProfile, tuple(), None, None, iter(self.items()))

    def add(self, component, date, reps):
        self[component].add(date, reps)

    def merge(self, tech_profile):
        assert isinstance(tech_profile, TechProfile)
        for component, exposure in tech_profile.items():
            assert exposure
            self[component].merge(exposure)


