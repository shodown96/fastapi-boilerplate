from fastcrud import FastCRUD

from models.token_blacklist import TokenBlacklist
from core.schemas import TokenBlacklistCreate, TokenBlacklistRead, TokenBlacklistUpdate

CRUDTokenBlacklist = FastCRUD[
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    TokenBlacklistRead,
]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
