def outsource_group_check(user):
    return user.groups.filter(name='outsource') or False