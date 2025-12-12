#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/datasets.py
#   Generator Datasets - Data pools for generation
#   Predefined datasets for synthetic data generation
#..............................................................

"""
Generator Datasets - Data Pools for Generation.

   Predefined datasets and generators for creating synthetic data.
   Provides data pools for various field types and generation functions.

   Datasets:

   Business Data:
   - BUSINESS_NAME_FIRST, BUSINESS_NAME_SECOND, BUSINESS_NAME_THIRD, COMPANY_FORMS
   - generate_business_name(): Compound business name (3 words + company form)

   Personal Data:
   - FIRST_NAMES, LAST_NAMES
   - generate_full_name(): First name + last name

   Location Data:
   - COUNTRIES, CITIES_SK, CITIES_CZ, CITIES_EU, ALL_CITIES
   - STREET_TYPES, STREET_NAMES
   - POSTAL_CODE_FORMATS
   - generate_country(), generate_city(), generate_street(), generate_postal_code()
   - generate_address(): Complete address (country + ZIP + city + street)

   Contact Data:
   - EMAIL_DOMAINS, PHONE_FORMATS
   - generate_email(): Email from first_name + last_name
   - generate_phone_number(): Phone number with country code

   Business Entities:
   - WORKING_PLACES, MATERIALS, RESOURCES
   - EQUIPMENT_TYPES, EQUIPMENT_BRANDS, EQUIPMENT_MODIFIERS
   - generate_working_place(), generate_material(), generate_resource()
   - generate_equipment(): Equipment name with type, brand, modifier

   User Data:
   - USER_ROLES: superadmin, admin, staff, editor, reader, adhoc
   - generate_user_role(): Random user role
   - generate_username(): Lowercase username from first_name + last_name
   - generate_photo_url(): Placeholder photo URL
   - generate_tag(): Random tag from predefined list

   Usage:
   ```python
   from sopira_magic.apps.generator.datasets import generate_business_name, generate_email
   company_name = generate_business_name()
   email = generate_email('John', 'Doe')
   ```
"""

import random
from typing import List


# Business names - compound 3 words + company form
BUSINESS_NAME_FIRST = [
    "American", "Indian", "Chinese", "Russian", "European", "Panamerican",
    "Slovakian", "German", "Viking", "Italian", "Spanish", "Global",
    "Arabian", "Polish", "British", "Dutch", "French", "Scandinavian",
    "Czech", "Nordic", "Continental", "Transcontinental", "Pacific", "Atlantic",
    "Eastern", "Western", "Northern", "Southern", "Central", "International",
]

BUSINESS_NAME_SECOND = [
    "Heavy", "Super", "Special", "New", "Big", "Ecological", "Innovative",
    "Common", "General", "New Science", "Singular", "Private", "Enhanced",
    "Raising Star", "National", "International", "Great", "Startup", "Advanced",
    "Dynamic", "Creative", "Future", "Modern", "NextGen", "Prime", "Pioneer",
    "Elite", "Premium", "Ultra", "Mega", "Pro", "Expert", "Master",
]

BUSINESS_NAME_THIRD = [
    "Industries", "Corporation", "Metal Industries", "Mining Industries",
    "Research", "Production", "Trading", "Exploitation", "Company",
    "Jointventure", "Investment", "Group", "Association", "Partners", "Holding",
    "Enterprises", "Works", "Solutions", "Technologies", "Systems", "Logistics",
    "Manufacturing", "Developments", "Innovations", "Ventures", "Dynamics",
    "Services", "Consulting", "Management", "Operations", "Resources",
]

COMPANY_FORMS = [
    "Ltd.", "Inc.", "LLC", "Corp.", "GmbH", "s.r.o.", "a.s.", "Sp. z o.o.",
    "S.A.", "S.L.", "B.V.", "AB", "Oy", "AS", "AG", "S.p.A.",
]


def generate_business_name() -> str:
    """Generate compound business name (3 words + company form)."""
    first = random.choice(BUSINESS_NAME_FIRST)
    second = random.choice(BUSINESS_NAME_SECOND)
    third = random.choice(BUSINESS_NAME_THIRD)
    form = random.choice(COMPANY_FORMS)
    return f"{first} {second} {third} {form}"


# First names
FIRST_NAMES = [
    "Carlos", "Ana", "Luis", "Sofia", "Miguel", "Isabella", "Juan", "Camila",
    "Diego", "Valentina", "Javier", "Lucia", "Pedro", "Gabriela", "Alvaro",
    "Peter", "Linda", "James", "Patricia", "Robert", "Jennifer", "Michael",
    "Elizabeth", "William", "Barbara", "David", "Susan", "Richard", "Jessica",
    "Jozef", "Mária", "Martin", "Katarína", "Zuzana", "Lukáš", "Anna",
    "Tomáš", "Eva", "Michal", "Monika", "Róbert", "Veronika", "Andrej", "Natalia",
    "Hannah", "Joseph", "Samantha", "Charles", "Olivia", "Daniel", "Sophia",
    "Norbert", "Klaus", "Helena", "Igor", "Renata", "Viktor", "Petra", "Joachim",
    "Sebastian", "Claudia", "Alexander", "Ursula", "Maximilian", "Anja", "Felix", "Bianca",
    "Emma", "Noah", "Oliver", "Ava", "Elijah", "Charlotte", "Lucas", "Amelia",
    "Mason", "Harper", "Ethan", "Evelyn", "Logan", "Abigail", "Jackson", "Emily",
]


# Last names
LAST_NAMES = [
    "Alvarez", "Gonzalez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Sanchez",
    "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Morales",
    "Schmidt", "Müller", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
    "Becker", "Hoffmann", "Schulz", "Koch", "Bauer", "Richter", "Klein", "Wolf",
    "Novak", "Kovacs", "Horvath", "Toth", "Szabo", "Varga", "Molnar", "Nagy",
    "Smirnov", "Ivanov", "Kuznetsov", "Popov", "Sokolov", "Lebedev", "Kozlov",
    "Petrov", "Semenov", "Egorov", "Pavlov", "Volkov", "Sidorov", "Mikhailov",
    "Kováč", "Horváth", "Baláž", "Tóth", "Farkaš", "Molnár",
    "Kiss", "Szabó", "Papp", "Mészáros", "Lakatos", "Vincze", "Kerekes", "Szalai",
    "Novák", "Dvořák", "Svoboda", "Novotný", "Černý", "Procházka", "Kučera", "Veselý",
    "Horák", "Beneš", "Pokorný", "Jelínek", "Smith", "Johnson", "Williams", "Brown",
    "Jones", "Garcia", "Miller", "Davis",
]


def generate_full_name() -> tuple[str, str]:
    """Generate first name and last name."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return first_name, last_name


# Working places
WORKING_PLACES = [
    "Main Entrance", "Warehouse", "Loading Dock", "Assembly Line",
    "Quality Control", "Research Lab", "Maintenance Area", "Office Block",
    "Cafeteria", "Parking Lot", "Storage Facility", "Shipping Area",
    "Receiving Area", "Production Floor", "Security Checkpoint",
    "Conference Room", "Break Room", "Restrooms", "IT Department", "HR Department",
    "Manufacturing Hall", "Packaging Area", "Testing Lab", "Tool Room",
    "Workshop", "Garage", "Dock", "Yard", "Factory Floor", "Control Room",
    "Boiler Room", "Cooling Tower", "Compressor Station", "Power Plant",
    "Water Treatment", "Waste Management", "Recycling Center", "Distribution Center",
]


def generate_working_place() -> str:
    """Generate working place name."""
    return random.choice(WORKING_PLACES)


# Materials
MATERIALS = [
    "Steel", "Aluminum", "Copper", "Iron", "Bronze", "Brass", "Titanium",
    "Plastic", "Rubber", "Glass", "Ceramic", "Concrete", "Wood", "Fabric",
    "Leather", "Paper", "Cardboard", "Foam", "Silicon", "Carbon Fiber",
    "Stainless Steel", "Galvanized Steel", "Carbon Steel", "Alloy Steel",
    "Polyethylene", "Polypropylene", "PVC", "Nylon", "Polyester", "Acrylic",
    "Marble", "Granite", "Limestone", "Sandstone", "Quartz", "Slate",
    "Cotton", "Wool", "Silk", "Linen", "Synthetic Fiber", "Bamboo",
]


def generate_material() -> str:
    """Generate material name."""
    return random.choice(MATERIALS)


# Resources
RESOURCES = [
    "Water", "Electricity", "Gas", "Oil", "Coal", "Natural Gas", "Solar Energy",
    "Wind Energy", "Hydroelectric", "Nuclear", "Biomass", "Geothermal",
    "Raw Materials", "Components", "Parts", "Supplies", "Inventory", "Stock",
    "Manpower", "Labor", "Expertise", "Knowledge", "Information", "Data",
    "Equipment", "Machinery", "Tools", "Vehicles", "Infrastructure", "Facilities",
    "Capital", "Funding", "Investment", "Budget", "Revenue", "Assets",
    "Time", "Space", "Capacity", "Bandwidth", "Storage", "Memory",
]


def generate_resource() -> str:
    """Generate resource name."""
    return random.choice(RESOURCES)


# Equipments
EQUIPMENT_TYPES = [
    "Machine", "Tool", "Device", "Apparatus", "Instrument", "Equipment",
    "Appliance", "Gadget", "Contraption", "Mechanism", "System", "Unit",
]

EQUIPMENT_BRANDS = [
    "Volvo", "Scania", "Man", "Cummins", "Renault", "Caterpillar", "Daewoo",
    "Hitachi", "Siemens", "Bosch", "ABB", "Schneider", "GE", "Honeywell",
    "Emerson", "Yokogawa", "Rockwell", "Omron", "Mitsubishi", "Fanuc",
    "Kuka", "ABB Robotics", "FANUC Robotics", "Universal Robots",
]

EQUIPMENT_MODIFIERS = [
    "Heavy", "Light", "Portable", "Stationary", "Automated", "Manual",
    "Precision", "Industrial", "Commercial", "Professional", "Standard",
    "Advanced", "High-Speed", "Low-Noise", "Energy-Efficient", "Compact",
    "Large-Scale", "Multi-Purpose", "Specialized", "Universal", "Custom",
]


def generate_equipment() -> str:
    """Generate equipment name."""
    modifier = random.choice(EQUIPMENT_MODIFIERS)
    brand = random.choice(EQUIPMENT_BRANDS)
    equipment_type = random.choice(EQUIPMENT_TYPES)
    return f"{modifier} {brand} {equipment_type}"


# Countries
COUNTRIES = [
    "Slovakia", "Czech Republic", "Poland", "Hungary", "Austria", "Germany",
    "France", "Italy", "Spain", "United Kingdom", "Netherlands", "Belgium",
    "Switzerland", "Sweden", "Norway", "Denmark", "Finland", "Portugal",
    "Greece", "Romania", "Bulgaria", "Croatia", "Serbia", "Slovenia",
    "United States", "Canada", "Mexico", "Brazil", "Argentina", "Chile",
    "Japan", "China", "South Korea", "India", "Australia", "New Zealand",
]


def generate_country() -> str:
    """Generate country name."""
    return random.choice(COUNTRIES)


# Cities
CITIES_SK = [
    "Bratislava", "Košice", "Prešov", "Žilina", "Banská Bystrica", "Nitra",
    "Trnava", "Trenčín", "Martin", "Poprad", "Prievidza", "Zvolen",
    "Považská Bystrica", "Michalovce", "Nové Zámky", "Spišská Nová Ves",
    "Komárno", "Humenné", "Levice", "Bardejov", "Liptovský Mikuláš",
]

CITIES_CZ = [
    "Prague", "Brno", "Ostrava", "Plzeň", "Liberec", "Olomouc",
    "Ústí nad Labem", "České Budějovice", "Hradec Králové", "Pardubice",
    "Zlín", "Havířov", "Kladno", "Most", "Opava", "Frýdek-Místek",
    "Karviná", "Jihlava", "Teplice", "Děčín",
]

CITIES_EU = [
    "Berlin", "Vienna", "Warsaw", "Budapest", "Paris", "Rome", "Madrid",
    "London", "Amsterdam", "Brussels", "Zurich", "Stockholm", "Oslo",
    "Copenhagen", "Helsinki", "Lisbon", "Athens", "Bucharest", "Sofia",
    "Zagreb", "Belgrade", "Ljubljana",
]

ALL_CITIES = CITIES_SK + CITIES_CZ + CITIES_EU


def generate_city() -> str:
    """Generate city name."""
    return random.choice(ALL_CITIES)


# Streets
STREET_TYPES = [
    "Street", "Avenue", "Road", "Boulevard", "Lane", "Drive", "Way",
    "Place", "Square", "Court", "Park", "Circle", "Terrace",
]

STREET_NAMES = [
    "Main", "First", "Second", "Third", "Fourth", "Fifth", "Oak", "Maple",
    "Pine", "Cedar", "Elm", "Park", "Church", "School", "Market", "High",
    "Broad", "Long", "Short", "New", "Old", "North", "South", "East", "West",
    "Central", "Union", "Washington", "Lincoln", "Roosevelt", "Churchill",
    "Freedom", "Liberty", "Independence", "Peace", "Victory", "Sunset",
    "Sunrise", "River", "Lake", "Hill", "Valley", "Bridge", "Station",
]


def generate_street() -> str:
    """Generate street name."""
    street_name = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    return f"{street_name} {street_type}"


# Postal codes (ZIP/PSC)
POSTAL_CODE_FORMATS = {
    "SK": lambda: f"{random.randint(800, 999)}{random.randint(10, 99)}",
    "CZ": lambda: f"{random.randint(100, 999)} {random.randint(10, 99)}",
    "PL": lambda: f"{random.randint(10, 99)}-{random.randint(100, 999)}",
    "DE": lambda: f"{random.randint(10000, 99999)}",
    "US": lambda: f"{random.randint(10000, 99999)}",
    "UK": lambda: f"{random.choice(['SW', 'NW', 'SE', 'NE', 'W', 'E', 'N', 'S'])}{random.randint(1, 20)} {random.randint(1, 9)}{random.choice(['AA', 'AB', 'CD', 'EF'])}",
}


def generate_postal_code(country: str = None) -> str:
    """Generate postal code (ZIP/PSC)."""
    if country:
        country_code = country[:2].upper() if len(country) > 2 else country.upper()
        if country_code in POSTAL_CODE_FORMATS:
            return POSTAL_CODE_FORMATS[country_code]()
    
    # Default: Slovak format
    return POSTAL_CODE_FORMATS["SK"]()


# Phone numbers
PHONE_FORMATS = {
    "SK": lambda: f"+421 {random.randint(900, 999)} {random.randint(100, 999)} {random.randint(100, 999)}",
    "CZ": lambda: f"+420 {random.randint(600, 799)} {random.randint(100, 999)} {random.randint(100, 999)}",
    "PL": lambda: f"+48 {random.randint(500, 899)} {random.randint(100, 999)} {random.randint(100, 999)}",
    "DE": lambda: f"+49 {random.randint(150, 999)} {random.randint(1000, 9999)}",
    "US": lambda: f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
    "UK": lambda: f"+44 {random.randint(7000, 7999)} {random.randint(100000, 999999)}",
}


def generate_phone_number(country: str = None) -> str:
    """Generate phone number."""
    if country:
        country_code = country[:2].upper() if len(country) > 2 else country.upper()
        # Map country names to codes
        country_map = {
            "SLOVAKIA": "SK", "CZECH": "CZ", "POLAND": "PL", "GERMANY": "DE",
            "UNITED STATES": "US", "UNITED KINGDOM": "UK", "UK": "UK",
        }
        for key, code in country_map.items():
            if key in country.upper():
                country_code = code
                break
        
        if country_code in PHONE_FORMATS:
            return PHONE_FORMATS[country_code]()
    
    # Default: Slovak format
    return PHONE_FORMATS["SK"]()


# Email domains
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "protonmail.com", "mail.com", "aol.com", "zoho.com", "yandex.com",
    "company.com", "business.com", "enterprise.com", "corp.com", "office.com",
    "example.com", "test.com", "demo.com",
]


def generate_email(first_name: str = None, last_name: str = None, domain: str = None) -> str:
    """Generate email address."""
    if first_name and last_name:
        # Use provided names
        base = f"{first_name.lower()}.{last_name.lower()}"
    elif first_name:
        base = first_name.lower()
    elif last_name:
        base = last_name.lower()
    else:
        # Generate random
        base = f"user{random.randint(1000, 9999)}"
    
    # Add random number if needed
    if random.choice([True, False]):
        base = f"{base}{random.randint(1, 99)}"
    
    domain = domain or random.choice(EMAIL_DOMAINS)
    return f"{base}@{domain}"


# Full address
def generate_address(country: str = None) -> dict:
    """Generate full address (country, ZIP, city, street)."""
    country_name = country or generate_country()
    postal_code = generate_postal_code(country_name)
    city = generate_city()
    street = generate_street()
    street_number = random.randint(1, 999)
    
    return {
        "country": country_name,
        "postal_code": postal_code,
        "city": city,
        "street": street,
        "street_number": street_number,
        "full_address": f"{street} {street_number}, {postal_code} {city}, {country_name}",
    }


# Positions (for Worker model - these are job positions, not authorization roles)
POSITIONS = [
    "admin", "manager", "supervisor", "operator", "technician", "engineer",
    "analyst", "coordinator", "specialist", "assistant", "director", "executive",
    "developer", "designer", "consultant", "auditor", "inspector", "controller",
    "user", "guest", "viewer", "editor", "moderator",
]


def generate_position() -> str:
    """Generate position name."""
    return random.choice(POSITIONS)


# User roles (authorization levels - same as thermal_eye)
USER_ROLES = ['superadmin', 'admin', 'staff', 'editor', 'reader', 'adhoc']


def generate_user_role() -> str:
    """Generate user role (authorization level)."""
    return random.choice(USER_ROLES)


# Usernames (lowercase)
def generate_username(first_name: str = None, last_name: str = None, index: int = None) -> str:
    """Generate lowercase username."""
    if first_name and last_name:
        # Use names: john.doe, jdoe, john.doe123
        variants = [
            f"{first_name.lower()}.{last_name.lower()}",
            f"{first_name.lower()}{last_name.lower()}",
            f"{first_name[0].lower()}{last_name.lower()}",
            f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}",
        ]
        return random.choice(variants)
    elif first_name:
        base = first_name.lower()
        if random.choice([True, False]):
            base = f"{base}{random.randint(1, 999)}"
        return base
    elif last_name:
        base = last_name.lower()
        if random.choice([True, False]):
            base = f"{base}{random.randint(1, 999)}"
        return base
    elif index:
        return f"user{index}"
    else:
        return f"user{random.randint(1000, 9999)}"


# Photos (URLs or placeholders)
PHOTO_SERVICES = [
    "https://i.pravatar.cc/150?img={}",
    "https://randomuser.me/api/portraits/{}/{}.jpg",
    "https://api.dicebear.com/7.x/avataaars/svg?seed={}",
    "https://ui-avatars.com/api/?name={}&size=150",
]


def generate_photo_url(name: str = None, seed: str = None, thumbnail: bool = False) -> str:
    """Generate photo URL (placeholder service)."""
    seed_value = seed or name or str(random.randint(1, 100))
    
    # Use different services randomly
    service = random.choice(PHOTO_SERVICES)
    
    if thumbnail:
        # For thumbnails, use smaller sizes
        if "pravatar.cc" in service:
            return service.replace("150", "64").format(random.randint(1, 70))
        elif "randomuser.me" in service:
            gender = random.choice(["men", "women"])
            return service.format(gender, random.randint(1, 99))
        elif "dicebear.com" in service:
            return service.replace("svg", "png").replace("avataaars", "avataaars").format(seed_value) + "&size=64"
        elif "ui-avatars.com" in service:
            name_param = name.replace(" ", "+") if name else seed_value
            return service.replace("150", "64").format(name_param)
    
    if "pravatar.cc" in service:
        return service.format(random.randint(1, 70))
    elif "randomuser.me" in service:
        gender = random.choice(["men", "women"])
        return service.format(gender, random.randint(1, 99))
    elif "dicebear.com" in service:
        return service.format(seed_value)
    elif "ui-avatars.com" in service:
        name_param = name.replace(" ", "+") if name else seed_value
        return service.format(name_param)
    
    return service.format(seed_value)


# Tags
TAG_POOL = [
    "Important", "ToCheck", "ToDo", "NightShift", "DayShift", "Front", "Back",
    "Hot", "Warm", "Cold", "Recheck", "QA", "Training", "Demo", "ProofAgain", "Suspicious",
    "Verified", "Urgent", "LowPriority", "HighPriority", "Maintenance", "Calibration",
    "Test", "Sample", "Archive", "Active", "Inactive", "Critical", "Normal", "Review",
    "FollowUp", "Completed", "Pending", "Delayed", "OnHold", "New", "Old", "Seasonal",
    "External", "Internal", "Remote", "Local", "Automated", "Manual", "VerifiedByQA", "NeedsApproval",
    "ForTraining", "ForDemo", "Prototype", "Final", "Draft", "Confidential", "Public", "Restricted",
    "Manager", "Employee", "Contractor", "Temporary", "Permanent", "FullTime", "PartTime",
    "Expert", "Beginner", "Intermediate", "Senior", "Junior", "Lead", "Team",
]


def generate_tags(count: int = None) -> list:
    """Generate list of tags."""
    if count is None:
        count = random.randint(1, 5)
    return random.sample(TAG_POOL, min(count, len(TAG_POOL)))


# IP Addresses
IP_PREFIXES = [
    "192.168.1",
    "192.168.0",
    "10.0.0",
    "10.0.1",
    "172.16.0",
    "172.16.1",
]


def generate_ip_address() -> str:
    """Generate valid private IP address."""
    prefix = random.choice(IP_PREFIXES)
    last_octet = random.randint(1, 254)  # Avoid 0 (network) and 255 (broadcast)
    return f"{prefix}.{last_octet}"

