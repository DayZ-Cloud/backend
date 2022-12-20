from libraries.jwt_controller import AccessVerifier, RefreshVerifier, Credentials

access_security = AccessVerifier()
refresh_security = RefreshVerifier()
JAC = Credentials