from datetime import datetime, timedelta


class TechProfile(defaultdict):
    '''
    TechProfile gather metrics attempting to evaluate a developer's skill level.
    Obviously, this will always be somewhat incomplete, and not fool proof.
    But the goal here is to get a good enough correlation that we can weed out
    most bad candidates or find out which areas people shine in.
    
    Metrics:  breadth & depth of knowledge, freshness.
    Derived metrics: experience (breadth*depth), readiness (breadth*freshness)
    As with most metrics, the number by itself is pretty useless.
    It is more useful when used as comparison tool.

    The basic element of comparison is the percentile in the population of developers.
    Another type of comparison is against a given technology context.
    From a client repository, we can run the same tech extraction code and determine
    very finely the technologies used.
    We can then compute the ranking of a set of devs precisely for these technologies,
    allowing a more accurate matchmaking.

    Breadth:
    Depth:

    Freshness is a metrics that attempts to capture how fresh a particular piece of knowledge is
    in the mind of a developer.
    The higher the number, the better we estimate it will be able to remember completely a given fact.
    This relates to notions of spaced repetition or spacing effect.
    For the same given fact, between 2 different developers, which one is more likely to remember it?
    This could be useful when looking for matches for a given client code base.
    From it, we can extract the technologies they used with high resolution (function level or less),
    and for each candidate, calculate an average freshness that is relevant only to these facts.

    Freshness = (number of repetitions)*(learning period)/(recall period)
    
    Number of repetitions:
    it's the number of times one has had to express a fact in code.

    Learning period:
    it's the length of time one has been exposed to a given fact.
    That would be the difference in time between the first time one has learnt a fact and the last time
    one has had to express it in code.
    If a fact has only been expressed once, we count that period as one day.

    Recall period:
    it's the time elapsed between now and the last time one expressed a fact.

    Freshness of 0 means 'unknown'.
    Freshness has no upper bound, although for a human, values have a practical upper bound in the sense
    that one can hardly have expressed repeatedly a single fact in code, every second of his life.

    Some examples to get a feel for freshness:

    Assuming one has expressed that a fact once, 10 years ago, the freshness would be:
    freshness = 1 * 1 / (10*365) = 0.0027.

    Assuming one has expressed the same fact in code 3 times per day, 5 days a week, over the course of one month (4 weeks),
    three months ago, we would have:
    freshness = (3*5*4) * 30 / 90 = 2

    '''

    def __init__(self):
        self.default_factory = list

    def __str__(self):
        return 'TechProfile(experience[{}], readiness[{}])'.format(self.experience, self.readiness)

    @property
    def breadth(self):
        return len(list(self.keys()))

    @property
    def depth(self):
        return sum(map(len, self.values()))

    @property
    def experience(self):
        return self.breadth * self.depth

    @property
    def freshness(self):
        freshnesses = []
        for dates in self.values():
            freshnesses.append(freshness(dates))
        # freshness is average over all technologies
        return  sum(freshnesses)/len(freshnesses)

    @property
    def readiness(self):
        return self.breadth * self.freshness

    def __reduce__(self):
        return (TechProfile, tuple(), None, None, iter(self.items()))

    def add(self, exposure):
        for component, dates in exposure.items():
            assert dates
            self[component].extend(dates)
            self[component].sort()

    def summarize(self, component=''):
        matching_keys = list(filter(lambda key: key.startswith(component), self.keys()))
        if not matching_keys:
            raise RuntimeError('Could not find any technology name starting with '+component)
        matching_dates = []
        freshnesses = []
        for key in matching_keys:
            dates = self[key]
            freshnesses.append(freshness(dates))
            matching_dates.extend(dates)
        breadth = len(matching_keys)
        depth = len(matching_dates)
        # freshness is average over all technologies
        average_freshness = sum(freshnesses)/len(freshnesses)
        return TechSummary(breadth, depth, average_freshness, breadth*depth, breadth*average_freshness)


TechSummary = namedtuple('TechSummary', ['breadth', 'depth', 'freshness', 'experience', 'readiness'])


def freshness(dates):
    learning_period = dates[-1] - dates[0] if len(dates) > 1 else timedelta(days=1)
    time_to_last_exposure = datetime.utcnow() - dates[-1]
    return len(dates)*learning_period/time_to_last_exposure


