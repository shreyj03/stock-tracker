# project/context_processors.py
# Shrey Jain, shreyj@bu.edu, 4/27/2026
# Context processors for the stock portfolio tracker application.

def profile_context(request):
    """Add the current user's project profile pk to the template context."""
    profile_pk = None
    if request.user.is_authenticated:
        try:
            profile_pk = request.user.project_profile.pk
        except:
            profile_pk = None
    return {'profile_pk': profile_pk}