from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import re

from app.utils.nickname_gen import generate_nickname

class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url

def validate_password(password: str) -> str:
    """
    Validate password meets security requirements:
    - Minimum 8 characters
    - Maximum 100 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(password) > 100:
        raise ValueError("Password must be at most 100 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")
    if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
        raise ValueError("Password must contain at least one special character")
    return password

def validate_bio_length(bio: Optional[str]) -> Optional[str]:
    """Validate bio length and content"""
    if bio is None:
        return bio
    if len(bio) > 500:
        raise ValueError("Bio must be at most 500 characters long")
    return bio.strip()

def validate_profile_picture_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    # Additional checks for profile picture URLs
    if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return url
    raise ValueError('Profile picture URL must end with .jpg, .jpeg, .png, or .gif')

def validate_email_format(email: str) -> str:
    """
    Additional email format validation beyond Pydantic's EmailStr
    """
    if not email:
        raise ValueError("Email is required")
    
    # Check length
    if len(email) > 255:
        raise ValueError("Email must be at most 255 characters long")
        
    # Check for common patterns
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
        
    # Check for common mistakes
    if '..' in email or email.startswith('.') or email.endswith('.'):
        raise ValueError("Invalid email format: consecutive dots not allowed")
        
    return email.lower()  # Normalize to lowercase

def validate_role_transition(current_role: UserRole, new_role: UserRole) -> bool:
    """
    Validate if a role transition is allowed based on role hierarchy
    """
    role_hierarchy = {
        UserRole.ANONYMOUS: [UserRole.AUTHENTICATED],
        UserRole.AUTHENTICATED: [UserRole.MANAGER],
        UserRole.MANAGER: [UserRole.ADMIN],
        UserRole.ADMIN: []
    }
    
    return new_role in role_hierarchy.get(current_role, [])

class UserBase(BaseModel):
    email: EmailStr = Field(
        ..., 
        example="john.doe@example.com",
        description="Email must be a valid format and unique in the system"
    )
    nickname: Optional[str] = Field(
        None, 
        min_length=3,
        max_length=30,
        pattern=None,  
        example=generate_nickname()
    )
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(
        None, 
        example="Experienced software developer specializing in web applications."
    )
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")

    @validator('nickname')
    def validate_nickname(cls, v):
        if v is None:
            return v
        if len(v) < 3:
            raise ValueError('Nickname must be at least 3 characters long')
        if len(v) > 30:
            raise ValueError('Nickname must be at most 30 characters long')
        if not v[0].isalnum():
            raise ValueError('Nickname must start with a letter or number')
        if '--' in v or '__' in v:
            raise ValueError('Nickname cannot contain consecutive hyphens or underscores')
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', v):
            raise ValueError('Nickname can only contain letters, numbers, underscores, and hyphens')
        return v

    @validator('bio')
    def validate_bio(cls, v):
        return validate_bio_length(v)

    @validator('profile_picture_url')
    def validate_profile_picture(cls, v):
        if v is not None:
            return validate_profile_picture_url(v)
        return v

    @validator('email')
    def validate_email(cls, v):
        return validate_email_format(v)

    _validate_social_urls = validator('linkedin_profile_url', 'github_profile_url', pre=True, allow_reuse=True)(validate_url)

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(
        ..., 
        min_length=8,
        max_length=100,
        example="SecureP@ss123"
    )

    @validator('password')
    def validate_password_requirements(cls, v):
        return validate_password(v)

class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(
        None, 
        example="john.doe@example.com",
        description="Email must be a valid format and unique in the system"
    )
    nickname: Optional[str] = Field(
        None, 
        min_length=3,
        max_length=30,
        pattern=None,  
        example="john_doe123"
    )
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(
        None, 
        example="Experienced software developer specializing in web applications."
    )
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] = Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")
    role: Optional[UserRole] = Field(
        None,
        description="User role in the system. Role transitions must follow the hierarchy."
    )

    @root_validator(pre=True)
    def check_update_fields(cls, values):
        # Ensure at least one field is provided
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        
        # Validate email if provided
        if 'email' in values and values['email']:
            values['email'] = validate_email_format(values['email'])
        
        # Handle other validations
        if 'profile_picture_url' in values and values['profile_picture_url']:
            validate_profile_picture_url(values['profile_picture_url'])
        
        if 'bio' in values and values['bio']:
            validate_bio_length(values['bio'])
            
        if 'role' in values and values['role']:
            if values['role'] not in [role.value for role in UserRole]:
                raise ValueError(f"Invalid role. Must be one of: {', '.join([role.value for role in UserRole])}")

        return values

class UserResponse(UserBase):
    id: uuid.UUID = Field(..., example=uuid.uuid4())
    role: UserRole = Field(default=UserRole.AUTHENTICATED, example="AUTHENTICATED")
    is_professional: Optional[bool] = Field(default=False, example=True)

    @validator('nickname')
    def validate_nickname(cls, v):
        if v is None:
            return v
        if len(v) < 3:
            raise ValueError('Nickname must be at least 3 characters long')
        if len(v) > 30:
            raise ValueError('Nickname must be at most 30 characters long')
        if not v[0].isalnum():
            raise ValueError('Nickname must start with a letter or number')
        if '--' in v or '__' in v:
            raise ValueError('Nickname cannot contain consecutive hyphens or underscores')
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', v):
            raise ValueError('Nickname can only contain letters, numbers, underscores, and hyphens')
        return v

class LoginRequest(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure*1234")

class ErrorResponse(BaseModel):
    error: str = Field(..., example="Not Found")
    details: Optional[str] = Field(None, example="The requested resource was not found.")

class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(..., example=[{
        "id": uuid.uuid4(), "nickname": generate_nickname(), "email": "john.doe@example.com",
        "first_name": "John", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "last_name": "Doe", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "profile_picture_url": "https://example.com/profiles/john.jpg", 
        "linkedin_profile_url": "https://linkedin.com/in/johndoe", 
        "github_profile_url": "https://github.com/johndoe"
    }])
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)