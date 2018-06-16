def user_allowed_society(user, target_society):
    # Superusers go straight ahead
    if user.is_superuser:
        return True

    # Checking that we're the same society
    if user.spfuser.society == target_society:
        return True

    # Checking whether the user is one of the societies
    if hasattr(target_society, 'all') and user.spfuser.society in target_society.all():
        return True

    return False


def user_society(request):
    return request.user.spfuser.society
