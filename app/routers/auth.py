import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

router = APIRouter()


# Auth0 Config
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-6mdq3tdvjb04tojd.us.auth0.com").strip()
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "redmane").strip()
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"


bearer_scheme = HTTPBearer()  # Use HTTP Bearer authentication scheme
# # Configure OAuth2 authentication, FastAPI will automatically parse the Bearer Token from the request
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token")

def get_auth0_public_key(token: str):
    """Fetch the public key from Auth0 JWKS endpoint."""
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    unverified_header = jwt.get_unverified_header(token)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Public key not found")

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """Verify Auth0 JWT token."""
    token = credentials.credentials
    try:
        public_key = get_auth0_public_key(token)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


@router.get("/auth/")
async def get_user(token: dict = Depends(verify_token)):
    """ Retrieve user information via Token """
    return {
        "user_id": token["sub"],
        "email": token.get("email"),
        "roles": token.get("realm_access", {}).get("roles", [])
    }
