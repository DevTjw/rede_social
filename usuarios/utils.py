def get_perfil_data(user):
    perfil = getattr(user, "perfil", None)

    foto_url = None
    if perfil and perfil.foto_perfil:
        foto_url = perfil.foto_perfil.url

    return {
        "username": user.username,
        "email": user.email,
        "foto": foto_url,
        "bio": perfil.bio if perfil else "",
    }
