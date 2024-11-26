import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserBase, UserUpdate, UserRole, validate_role_transition
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

def test_valid_role_transitions():
    """Test allowed role transitions"""
    # Test valid role transitions
    assert validate_role_transition(UserRole.ANONYMOUS, UserRole.AUTHENTICATED) is True
    assert validate_role_transition(UserRole.AUTHENTICATED, UserRole.MANAGER) is True
    assert validate_role_transition(UserRole.MANAGER, UserRole.ADMIN) is True

def test_invalid_role_transitions():
    """Test disallowed role transitions"""
    # Test invalid role transitions
    assert validate_role_transition(UserRole.ANONYMOUS, UserRole.ADMIN) is False
    assert validate_role_transition(UserRole.AUTHENTICATED, UserRole.ADMIN) is False
    assert validate_role_transition(UserRole.ADMIN, UserRole.MANAGER) is False  # Can't demote
    assert validate_role_transition(UserRole.MANAGER, UserRole.AUTHENTICATED) is False  # Can't demote

def test_role_update_validation():
    """Test role validation in UserUpdate schema"""
    # Valid role update
    update = UserUpdate(role=UserRole.AUTHENTICATED)
    assert update.role == UserRole.AUTHENTICATED

    # Invalid role value
    with pytest.raises(ValueError, match="Invalid role"):
        UserUpdate(role="INVALID_ROLE")

@pytest.mark.asyncio
async def test_role_update_service(db_session: AsyncSession, email_service):
    """Test role updates through user service"""
    # Create a user with ANONYMOUS role
    user_data = {
        "email": "test.role@example.com",
        "password": "SecurePass123!"
    }
    user = await UserService.create(db_session, user_data, email_service)
    assert user is not None
    assert user.role == UserRole.AUTHENTICATED  # Default role

    # Valid role update: AUTHENTICATED -> MANAGER
    update_result = await UserService.update(
        db_session,
        user.id,
        {"role": UserRole.MANAGER.value}
    )
    assert update_result is not None
    assert update_result.role == UserRole.MANAGER

    # Invalid role update: MANAGER -> ANONYMOUS (not allowed)
    invalid_update = await UserService.update(
        db_session,
        user.id,
        {"role": UserRole.ANONYMOUS.value}
    )
    assert invalid_update is None  # Update should fail

@pytest.mark.asyncio
async def test_multiple_role_updates(db_session: AsyncSession, email_service):
    """Test multiple role transitions"""
    # Create initial user
    user_data = {
        "email": "role.test@example.com",
        "password": "SecurePass123!"
    }
    user = await UserService.create(db_session, user_data, email_service)
    assert user is not None
    initial_role = user.role

    # Test progression through roles
    role_progression = [
        UserRole.AUTHENTICATED,
        UserRole.MANAGER,
        UserRole.ADMIN
    ]

    current_role = initial_role
    for next_role in role_progression:
        if validate_role_transition(current_role, next_role):
            update_result = await UserService.update(
                db_session,
                user.id,
                {"role": next_role.value}
            )
            assert update_result is not None
            assert update_result.role == next_role
            current_role = next_role

@pytest.mark.asyncio
async def test_role_update_with_other_fields(db_session: AsyncSession, email_service):
    """Test role update combined with other field updates"""
    # Create user
    user_data = {
        "email": "combined.test@example.com",
        "password": "SecurePass123!"
    }
    user = await UserService.create(db_session, user_data, email_service)
    assert user is not None

    # Update role and other fields simultaneously
    update_data = {
        "role": UserRole.MANAGER.value,
        "nickname": "test_manager",
        "bio": "A test manager bio"
    }
    
    update_result = await UserService.update(
        db_session,
        user.id,
        update_data
    )
    assert update_result is not None
    assert update_result.role == UserRole.MANAGER
    assert update_result.nickname == "test_manager"
    assert update_result.bio == "A test manager bio"