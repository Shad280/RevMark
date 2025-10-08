from fastapi import APIRouter

router = APIRouter()

from .v1 import auth, users, escrow, messages, payments, uploads

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(escrow.router, prefix="/escrow", tags=["escrow"])
router.include_router(messages.router, prefix="/messages", tags=["messages"])
router.include_router(payments.router, prefix="/payments", tags=["payments"])
router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])