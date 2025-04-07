def user_context(request):
    return {
        'current_user': request.user,
        'user_id': request.user.id if request.user.is_authenticated else None
    }