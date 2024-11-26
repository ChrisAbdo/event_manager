import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserBase, UserUpdate

def test_valid_bio():
    # Test valid bio cases
    user = UserBase(email="test@example.com", bio="A valid bio")
    assert user.bio == "A valid bio"
    
    # Test empty bio
    user = UserBase(email="test@example.com", bio=None)
    assert user.bio is None
    
    # Test bio with whitespace
    user = UserBase(email="test@example.com", bio="  Bio with spaces  ")
    assert user.bio == "Bio with spaces"

def test_invalid_bio():
    # Test bio exceeding max length
    long_bio = "x" * 501
    with pytest.raises(ValueError, match="Bio must be at most 500 characters long"):
        UserBase(email="test@example.com", bio=long_bio)

def test_valid_profile_picture_urls():
    valid_urls = [
        "https://example.com/photo.jpg",
        "http://test.com/image.png",
        "https://subdomain.site.com/path/pic.jpeg",
        "https://site.com/image.gif"
    ]
    
    for url in valid_urls:
        user = UserBase(email="test@example.com", profile_picture_url=url)
        assert user.profile_picture_url == url

def test_invalid_profile_picture_urls():
    invalid_urls = [
        "not-a-url",
        "ftp://example.com/photo.jpg",
        "https://example.com/photo.pdf",
        "https://example.com/photo.doc",
        "https://example.com/photo",
    ]
    
    for url in invalid_urls:
        with pytest.raises(ValueError):
            UserBase(email="test@example.com", profile_picture_url=url)

def test_valid_social_urls():
    user = UserBase(
        email="test@example.com",
        linkedin_profile_url="https://linkedin.com/in/johndoe",
        github_profile_url="https://github.com/johndoe"
    )
    assert user.linkedin_profile_url == "https://linkedin.com/in/johndoe"
    assert user.github_profile_url == "https://github.com/johndoe"

def test_invalid_social_urls():
    with pytest.raises(ValueError, match="Invalid URL format"):
        UserBase(
            email="test@example.com",
            linkedin_profile_url="not-a-url"
        )
    
    with pytest.raises(ValueError, match="Invalid URL format"):
        UserBase(
            email="test@example.com",
            github_profile_url="invalid-github-url"
        )

def test_user_update_validation():
    # Test valid update with single field
    update = UserUpdate(bio="New bio")
    assert update.bio == "New bio"
    
    # Test valid update with multiple fields
    update = UserUpdate(
        bio="New bio",
        profile_picture_url="https://example.com/new.jpg",
        linkedin_profile_url="https://linkedin.com/in/newprofile"
    )
    assert update.bio == "New bio"
    assert update.profile_picture_url == "https://example.com/new.jpg"
    
    # Test empty update
    with pytest.raises(ValueError, match="At least one field must be provided for update"):
        UserUpdate()
    
    # Test invalid field combinations
    with pytest.raises(ValueError):
        UserUpdate(profile_picture_url="invalid-url")