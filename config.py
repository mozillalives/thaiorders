

webapp2_config = {}
webapp2_config['webapp2_extras.sessions'] = {
    'secret_key': 'Nicks th4i ord3rs',
    }
webapp2_config['webapp2_extras.auth'] = {
    'user_model': 'models.models.User',
    'cookie_name': 'session_name'
}
