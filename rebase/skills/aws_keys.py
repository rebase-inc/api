

def profile_key(user):
    return 'user-profiles/{user}/data'.format(user=user)


def old_profile_key(user):
    return profile_key(user)+'_old'


def level_key(level):
    return 'population/'+level 


