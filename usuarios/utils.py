def get_perfil_data(user):
    perfil = getattr(user, "perfil", None)
    return {
        "username": user.username,
        "email": user.email,
        "foto": getattr(perfil.foto_perfil, "url", None),
        "bio": getattr(perfil, "bio", ""),
    }