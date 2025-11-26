# Generator Datasets - Usage Examples

## Contact Information Datasets

### Email
```python
'email': {
    'type': 'dataset',
    'dataset': 'email',
    # Optional parameters:
    'first_name': 'John',      # Use specific first name
    'last_name': 'Doe',        # Use specific last name
    'domain': 'company.com',   # Use specific domain
}
```

### Phone Number
```python
'phone': {
    'type': 'dataset',
    'dataset': 'phone',
    # Optional parameter:
    'country': 'Slovakia',     # Country-specific format (SK, CZ, PL, DE, US, UK)
}
```

### Address Components
```python
'country': {
    'type': 'dataset',
    'dataset': 'country',
}

'city': {
    'type': 'dataset',
    'dataset': 'city',
}

'street': {
    'type': 'dataset',
    'dataset': 'street',
}

'postal_code': {
    'type': 'dataset',
    'dataset': 'postal_code',
    # Optional parameter:
    'country': 'Slovakia',     # Country-specific format
}
```

### Full Address
```python
'address': {
    'type': 'dataset',
    'dataset': 'address',
    # Optional parameters:
    'country': 'Slovakia',     # Specific country
    'as_dict': False,          # True returns dict, False returns string
}
```

Returns string format: `"Main Street 123, 81101 Bratislava, Slovakia"`
Or dict format (if `as_dict: True`):
```python
{
    'country': 'Slovakia',
    'postal_code': '81101',
    'city': 'Bratislava',
    'street': 'Main Street',
    'street_number': 123,
    'full_address': 'Main Street 123, 81101 Bratislava, Slovakia'
}
```

## Supported Countries

Phone and postal code formats support:
- Slovakia (SK) - `+421 900 123 456`, `81101`
- Czech Republic (CZ) - `+420 600 123 456`, `100 00`
- Poland (PL) - `+48 500 123 456`, `12-345`
- Germany (DE) - `+49 150 1234567`, `12345`
- United States (US) - `+1 (555) 123-4567`, `12345`
- United Kingdom (UK) - `+44 7000 123456`, `SW1A 1AA`

## Example: Complete Contact Generation

```python
'fields': {
    'first_name': {
        'type': 'dataset',
        'dataset': 'first_name',
    },
    'last_name': {
        'type': 'dataset',
        'dataset': 'last_name',
    },
    'email': {
        'type': 'dataset',
        'dataset': 'email',
        # Will use first_name and last_name from context automatically
    },
    'phone': {
        'type': 'dataset',
        'dataset': 'phone',
        'country': 'Slovakia',
    },
    'country': {
        'type': 'dataset',
        'dataset': 'country',
    },
    'city': {
        'type': 'dataset',
        'dataset': 'city',
    },
    'postal_code': {
        'type': 'dataset',
        'dataset': 'postal_code',
        # Will use country from context automatically
    },
    'street': {
        'type': 'dataset',
        'dataset': 'street',
    },
    'address': {
        'type': 'dataset',
        'dataset': 'address',
        # Will use country from context automatically
    },
}
```

