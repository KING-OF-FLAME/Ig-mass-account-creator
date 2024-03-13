from faker import Faker


def generate_account_details():
    fake = Faker('en_US')
    
    base_username = fake.user_name()
    full_name = fake.name()
    bio = fake.text(max_nb_chars=150)
    
    # For Instagram display, prefix with "@"
    instagram_username = f"@{base_username}"
    
    # Don't prefix base_username with "@" for email creation or other uses
    password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    
    user_details = {
        'full_name': full_name,
        'username': base_username,  # Use base_username without "@" for internal/technical uses
        'instagram_username': instagram_username,  # Use instagram_username for display purposes
        'bio': bio,
        'password': password
    }
    
    return user_details
