# Authentication settings
AUTH_USER_MODEL = 'CCC.User'

AUTHENTICATION_BACKENDS = [
    'CCC.auth.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True

# Login URLs
LOGIN_URL = 'signin'  # Change from '/accounts/login/'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'signin'

# Add to MIDDLEWARE if not present
MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ...
]