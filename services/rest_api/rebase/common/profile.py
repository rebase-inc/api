from contextlib import contextmanager
from cProfile import Profile
from pstats import Stats


@contextmanager
def profiling(sort_stats_keys=('cumulative',), print_stats_args=(.1, 'api\/rebase')):
    '''
    Prints a profile of the code executed in a 'with profiling()' statement

    Example:
    with profiling():
        my_slow_function()

    '''
    profile = Profile()
    profile.enable()
    yield
    profile.disable()
    stats = Stats(profile)
    stats.sort_stats(*sort_stats_keys)
    # print first 10% and only show my code
    stats.print_stats(*print_stats_args)
    #import pdb; pdb.set_trace()
