import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserCreate

@pytest.mark.asyncio
async def test_valid_passwords():
    valid_passwords = [
        "SecureP@ss123",
        "MyP@ssw0rd",
        "C0mpl3x!Pass",
        "Str0ng#P@ssword",
        "Test1ng@Password"
    ]
    
    for password in valid_passwords:
        user = UserCreate(
            email="test@example.com",
            password=password,
            nickname="testuser"
        )
        assert user.password == password

@pytest.mark.asyncio
async def test_password_too_short():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="short1!",
            nickname="testuser"
        )
    assert "String should have at least 8 characters" in str(exc_info.value)

@pytest.mark.asyncio
async def test_password_too_long():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="A" * 101,
            nickname="testuser"
        )
    assert "String should have at most 100 characters" in str(exc_info.value)

@pytest.mark.asyncio
async def test_password_no_uppercase():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="lowercase1!",
            nickname="testuser"
        )
    assert "Password must contain at least one uppercase letter" in str(exc_info.value)

@pytest.mark.asyncio
async def test_password_no_lowercase():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="UPPERCASE1!",
            nickname="testuser"
        )
    assert "Password must contain at least one lowercase letter" in str(exc_info.value)

@pytest.mark.asyncio
async def test_password_no_number():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="NoNumber!@",
            nickname="testuser"
        )
    assert "Password must contain at least one number" in str(exc_info.value)

@pytest.mark.asyncio
async def test_password_no_special():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@example.com",
            password="NoSpecial123",
            nickname="testuser"
        )
    assert "Password must contain at least one special character" in str(exc_info.value)