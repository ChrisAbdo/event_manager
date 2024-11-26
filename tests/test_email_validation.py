import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserBase, UserUpdate, UserCreate
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

def test_valid_email_formats():
    """Test various valid email formats"""
    valid_emails = [
        "user@example.com",
        "user.name@example.com",
        "user+label@example.com",
        "user123@example.co.uk",
        "first.last@subdomain.example.com",
        "user@example-domain.com",
        "user_name@example.com"
    ]
    
    for email in valid_emails:
        user = UserBase(email=email)
        assert user.email == email.lower()  # Should be normalized to lowercase

def test_invalid_email_formats():
    """Test various invalid email formats"""
    invalid_emails = [
        "",  # Empty
        "notanemail",  # No @ symbol
        "@example.com",  # No local part
        "user@",  # No domain
        "user@.",  # Invalid domain
        "user@example",  # No TLD
        "user..name@example.com",  # Consecutive dots
        "user@example..com",  # Consecutive dots in domain
        ".user@example.com",  # Starting with dot
        "user.@example.com",  # Ending with dot
        "user@example.c",  # TLD too short
        "a" * 246 + "@example.com"  # Too long (over 255 chars)
    ]
    
    for email in invalid_emails:
        with pytest.raises(ValidationError):
            UserBase(email=email)

def test_email_normalization():
    """Test that emails are normalized to lowercase"""
    mixed_case_email = "User.Name@Example.COM"
    user = UserBase(email=mixed_case_email)
    assert user.email == "user.name@example.com"

def test_email_update_validation():
    """Test email validation in UserUpdate schema"""
    # Valid update
    update = UserUpdate(email="new.email@example.com")
    assert update.email == "new.email@example.com"
    
    # Invalid update
    with pytest.raises(ValidationError):
        UserUpdate(email="invalid.email@")

@pytest.mark.asyncio
async def test_duplicate_email_creation(test_db_session: AsyncSession):
    """Test that creating a user with duplicate email fails"""
    # Create first user
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    user1 = await UserService.create(test_db_session, user_data, None)
    assert user1 is not None
    
    # Try to create second user with same email
    user2 = await UserService.create(test_db_session, user_data, None)
    assert user2 is None  # Should fail due to duplicate email

@pytest.mark.asyncio
async def test_duplicate_email_update(test_db_session: AsyncSession):
    """Test that updating a user with duplicate email fails"""
    # Create first user
    user1_data = {
        "email": "user1@example.com",
        "password": "SecurePass123!"
    }
    user1 = await UserService.create(test_db_session, user1_data, None)
    assert user1 is not None
    
    # Create second user
    user2_data = {
        "email": "user2@example.com",
        "password": "SecurePass123!"
    }
    user2 = await UserService.create(test_db_session, user2_data, None)
    assert user2 is not None
    
    # Try to update second user with first user's email
    update_result = await UserService.update(
        test_db_session,
        user2.id,
        {"email": "user1@example.com"}
    )
    assert update_result is None  # Should fail due to duplicate email