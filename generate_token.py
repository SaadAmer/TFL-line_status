# generate_token.py
import jwt, time

secret = "super-long-random-dev-secret"
now = int(time.time())
days = 30

claims = {
    "sub": "svc:interviewer",
    "iss": "wovenlight-dev",
    "aud": "wovenlight-api",
    "iat": now,
    "exp": now + days * 24 * 3600,
    "scope": "tasks:create tasks:read tasks:update tasks:delete"
}

token = jwt.encode(claims, secret, algorithm="HS256")
print(token)
