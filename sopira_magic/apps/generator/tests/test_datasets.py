#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/tests/test_datasets.py
#   Generator Datasets Tests
#   Tests for datasets.py module
#..............................................................

"""
   Generator Datasets Tests.

   Unit tests for dataset generation functions.
   Tests data generation from predefined datasets.
"""

import pytest
import re
from sopira_magic.apps.generator.datasets import (
    generate_business_name,
    generate_full_name,
    generate_email,
    generate_phone_number,
    generate_address,
    generate_user_role,
    generate_username,
    generate_photo_url,
    generate_tags,
    generate_working_place,
    generate_material,
    generate_resource,
    generate_equipment,
    generate_country,
    generate_city,
    generate_street,
    generate_postal_code,
    USER_ROLES,
)


class TestBusinessNameGeneration:
    """Test suite for business name generation."""

    def test_generate_business_name_format(self):
        """Test business name has correct format (3 words + company form)."""
        name = generate_business_name()
        
        # Should have 4 parts (3 words + form)
        parts = name.split()
        assert len(parts) >= 4

    def test_generate_business_name_contains_form(self):
        """Test business name contains company form."""
        # Generate multiple names to increase chance of finding form
        names = [generate_business_name() for _ in range(20)]
        
        # At least one should contain common company forms
        forms = ['Ltd.', 'Inc.', 'LLC', 'Corp.', 'GmbH', 's.r.o.', 'a.s.']
        assert any(any(form in name for form in forms) for name in names)

    def test_generate_business_name_randomness(self):
        """Test business names are different on multiple calls."""
        names = [generate_business_name() for _ in range(10)]
        
        # Should have some variety (not all same)
        assert len(set(names)) > 1


class TestPersonalNameGeneration:
    """Test suite for personal name generation."""

    def test_generate_full_name_returns_tuple(self):
        """Test generate_full_name returns tuple of two strings."""
        first, last = generate_full_name()
        
        assert isinstance(first, str)
        assert isinstance(last, str)
        assert len(first) > 0
        assert len(last) > 0

    def test_generate_full_name_randomness(self):
        """Test full names are different on multiple calls."""
        names = [generate_full_name() for _ in range(10)]
        
        # Should have some variety
        assert len(set(names)) > 1


class TestEmailGeneration:
    """Test suite for email generation."""

    def test_generate_email_format(self):
        """Test email has valid format."""
        email = generate_email('John', 'Doe')
        
        assert '@' in email
        assert '.' in email.split('@')[1]  # Domain has TLD
        assert 'john' in email.lower()
        assert 'doe' in email.lower()

    def test_generate_email_lowercase(self):
        """Test email is lowercase."""
        email = generate_email('John', 'Doe')
        
        assert email == email.lower()

    def test_generate_email_without_names(self):
        """Test email generation without names."""
        email = generate_email()
        
        assert '@' in email
        assert '.' in email.split('@')[1]


class TestPhoneNumberGeneration:
    """Test suite for phone number generation."""

    def test_generate_phone_number_format(self):
        """Test phone number has valid format."""
        phone = generate_phone_number()
        
        # Should contain digits and possibly + or spaces
        assert any(char.isdigit() for char in phone)
        assert len(phone) >= 9  # Minimum phone length

    def test_generate_phone_number_randomness(self):
        """Test phone numbers are different on multiple calls."""
        phones = [generate_phone_number() for _ in range(10)]
        
        # Should have some variety
        assert len(set(phones)) > 1


class TestAddressGeneration:
    """Test suite for address generation."""

    def test_generate_address_contains_components(self):
        """Test address contains all components."""
        address = generate_address()
        
        # generate_address returns a dict, not a string
        assert isinstance(address, dict)
        assert 'country' in address or 'full_address' in address
        # Should have multiple components
        assert len(address) >= 3

    def test_generate_address_randomness(self):
        """Test addresses are different on multiple calls."""
        addresses = [generate_address() for _ in range(10)]
        
        # Should have some variety (compare full_address strings)
        address_strings = [addr.get('full_address', str(addr)) for addr in addresses]
        assert len(set(address_strings)) > 1


class TestUserRoleGeneration:
    """Test suite for user role generation."""

    def test_generate_user_role_valid(self):
        """Test generated role is from valid roles list."""
        role = generate_user_role()
        
        assert role in USER_ROLES

    def test_generate_user_role_randomness(self):
        """Test roles are different on multiple calls (if multiple roles exist)."""
        roles = [generate_user_role() for _ in range(20)]
        
        # Should have some variety if multiple roles exist
        if len(USER_ROLES) > 1:
            assert len(set(roles)) > 1


class TestUsernameGeneration:
    """Test suite for username generation."""

    def test_generate_username_lowercase(self):
        """Test username is lowercase."""
        username = generate_username('John', 'Doe')
        
        assert username == username.lower()

    def test_generate_username_format(self):
        """Test username format."""
        username = generate_username('John', 'Doe')
        
        # Username can be in various formats: johndoe, jdoe, john.doe, etc.
        # Just check it's lowercase and contains parts of the name
        assert username == username.lower()
        assert ' ' not in username
        # Should contain at least first letter of first or last name
        assert 'j' in username or 'd' in username

    def test_generate_username_without_names(self):
        """Test username generation without names."""
        username = generate_username()
        
        assert isinstance(username, str)
        assert len(username) > 0
        assert username == username.lower()


class TestPhotoUrlGeneration:
    """Test suite for photo URL generation."""

    def test_generate_photo_url_format(self):
        """Test photo URL has valid format."""
        url = generate_photo_url()
        
        # Should be a URL-like string
        assert isinstance(url, str)
        assert len(url) > 0

    def test_generate_photo_url_randomness(self):
        """Test photo URLs are different on multiple calls."""
        urls = [generate_photo_url() for _ in range(10)]
        
        # Should have some variety
        assert len(set(urls)) > 1


class TestTagGeneration:
    """Test suite for tag generation."""

    def test_generate_tags_returns_list(self):
        """Test generate_tags returns a list."""
        tags = generate_tags()
        
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_generate_tags_with_count(self):
        """Test generate_tags with count parameter."""
        tags = generate_tags(count=5)
        
        assert isinstance(tags, list)
        assert len(tags) == 5

    def test_generate_tags_randomness(self):
        """Test tags are different on multiple calls."""
        tags1 = generate_tags(count=10)
        tags2 = generate_tags(count=10)
        
        # Should have some variety (not all same)
        assert tags1 != tags2 or len(set(tags1)) > 1


class TestBusinessEntityGeneration:
    """Test suite for business entity generation."""

    def test_generate_working_place(self):
        """Test working place generation."""
        place = generate_working_place()
        
        assert isinstance(place, str)
        assert len(place) > 0

    def test_generate_material(self):
        """Test material generation."""
        material = generate_material()
        
        assert isinstance(material, str)
        assert len(material) > 0

    def test_generate_resource(self):
        """Test resource generation."""
        resource = generate_resource()
        
        assert isinstance(resource, str)
        assert len(resource) > 0

    def test_generate_equipment(self):
        """Test equipment generation."""
        equipment = generate_equipment()
        
        assert isinstance(equipment, str)
        assert len(equipment) > 0


class TestLocationGeneration:
    """Test suite for location generation."""

    def test_generate_country(self):
        """Test country generation."""
        country = generate_country()
        
        assert isinstance(country, str)
        assert len(country) > 0

    def test_generate_city(self):
        """Test city generation."""
        city = generate_city()
        
        assert isinstance(city, str)
        assert len(city) > 0

    def test_generate_street(self):
        """Test street generation."""
        street = generate_street()
        
        assert isinstance(street, str)
        assert len(street) > 0

    def test_generate_postal_code(self):
        """Test postal code generation."""
        postal_code = generate_postal_code()
        
        assert isinstance(postal_code, str)
        assert len(postal_code) > 0
        # Should contain digits
        assert any(char.isdigit() for char in postal_code)

