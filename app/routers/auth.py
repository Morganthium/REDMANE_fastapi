import os
from functools import lru_cache

import httpx
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")

if not AUTH0_DOMAIN:
    raise RuntimeError("AUTH0_DOMAIN environment variable is not set — add it to your .env file")
if not AUTH0_AUDIENCE:
    raise RuntimeError("AUTH0_AUDIENCE environment variable is not set — add it to your .env file")

AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"

bearer_scheme = HTTPBearer()


@lru_cache(maxsize=1)
def get_jwks():
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def get_public_key(token: str):
    jwks = get_jwks()
    header = jwt.get_unverified_header(token)
    key = next(
        (k for k in jwks["keys"] if k["kid"] == header["kid"]),
        None
    )
    if key is None:
        raise HTTPException(status_code=401, detail="Signing key not found")
    return key


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    token = credentials.credentials
    try:
        public_key = get_public_key(token)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=AUTH0_ISSUER
        )
        if not payload.get("email"):
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"https://{AUTH0_DOMAIN}/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                payload["email"] = r.json().get("email")
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@router.get("/auth/")
async def get_user(token: dict = Depends(verify_token)):
    return {
        "user_id": token.get("sub"),
        "email": token.get("email"),
        "roles": token.get("realm_access", {}).get("roles", [])
    }