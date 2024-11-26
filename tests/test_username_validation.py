import pytest
from app.schemas.user_schemas import UserBase
from pydantic import ValidationError

@pytest.mark.asyncio
async def test_valid_nickname():
    valid_nicknames = [
        "john_doe123",
        "user_123",
        "coder_42",
        "test_user",
        "a-b-c",
        "123user",
        "Dev_Master"
    ]
    
    for nickname in valid_nicknames:
        user = UserBase(email="test@example.com", nickname=nickname)
        assert user.nickname == nickname

@pytest.mark.asyncio
async def test_invalid_nickname():
    invalid_nicknames = [
        "jo",  # too short
        "a" * 31,  # too long
        "user@123",  # invalid character
        "test user",  # contains space
        "user#123",  # invalid character
        "_start_underscore",  # starts with special char
        "-start-hyphen",  # starts with special char
        "double__underscore",  # consecutive underscores
        "double--hyphen",  # consecutive hyphens
        "!invalid",  # invalid start character
        "user name",  # contains space
        "user.name",  # contains period
    ]
    
    for nickname in invalid_nicknames:
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", nickname=nickname)

@pytest.mark.asyncio
async def test_nickname_error_messages():
    # Test specific error messages
    with pytest.raises(ValidationError) as exc_info:
        UserBase(email="test@example.com", nickname="_invalid")
    assert "Nickname must start with a letter or number" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        UserBase(email="test@example.com", nickname="test__user")
    assert "Nickname cannot contain consecutive hyphens or underscores" in str(exc_info.value)