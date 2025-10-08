from pydantic import BaseModel, EmailStr, constr, validator

class UserValidator(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)

    @validator('username')
    def username_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('Username must not contain spaces')
        return v

class EscrowValidator(BaseModel):
    title: constr(min_length=1, max_length=100)
    description: constr(min_length=1, max_length=500)
    budget: float

class MessageValidator(BaseModel):
    content: constr(min_length=1, max_length=1000)
    attachment_url: str = None

    @validator('attachment_url')
    def validate_attachment_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Attachment URL must be a valid URL')
        return v

class PaymentValidator(BaseModel):
    amount: float
    currency: constr(min_length=3, max_length=3)  # e.g., 'USD', 'EUR'