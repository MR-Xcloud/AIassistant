"""
Company products information module.
This contains details about products and projects developed by WebMobril.
"""

# Dictionary of company products and projects
COMPANY_PRODUCTS = {
    # Major products
    "Products": [
        {
            "name": "Cabzy",
            "description": "A taxi booking and dispatch solution that helps taxi companies manage their fleet and bookings efficiently. It includes features for real-time tracking, automated dispatching, and payment processing.",
            "type": "Mobile App & Web Platform",
            "industry": "Transportation"
        },
        {
            "name": "Foodzi",
            "description": "A comprehensive food delivery platform connecting restaurants with customers for online ordering and delivery. It includes features for menu management, order tracking, and delivery logistics.",
            "type": "Mobile App & Web Platform",
            "industry": "Food & Beverage"
        },
        {
            "name": "Medica",
            "description": "A healthcare management system for hospitals and clinics to manage patient records, appointments, and billing. It streamlines healthcare operations and improves patient care.",
            "type": "Web Application",
            "industry": "Healthcare"
        },
        {
            "name": "EduLearn",
            "description": "An e-learning platform for schools and educational institutions to conduct online classes and manage coursework. It includes features for virtual classrooms, assignment submission, and progress tracking.",
            "type": "Web & Mobile Application",
            "industry": "Education"
        },
        {
            "name": "ShopEasy",
            "description": "An e-commerce solution for businesses to set up their online stores and manage inventory and orders. It includes features for product catalog management, shopping cart, and payment processing.",
            "type": "Web & Mobile Application",
            "industry": "Retail"
        },
        {
            "name": "TravelBuddy",
            "description": "A travel planning and booking application that helps users find and book flights, hotels, and activities. It includes features for itinerary planning and travel recommendations.",
            "type": "Mobile App",
            "industry": "Travel & Tourism"
        },
        {
            "name": "PropertyPro",
            "description": "A real estate management platform for property listings, virtual tours, and agent management. It helps buyers find properties and sellers list their properties efficiently.",
            "type": "Web & Mobile Application",
            "industry": "Real Estate"
        },
        {
            "name": "FinTrack",
            "description": "A financial management application for personal and business finance tracking. It includes features for expense tracking, budgeting, and financial reporting.",
            "type": "Web & Mobile Application",
            "industry": "Finance"
        },
        {
            "name": "FitLife",
            "description": "A fitness and wellness application for workout tracking, nutrition planning, and health monitoring. It helps users achieve their fitness goals with personalized plans.",
            "type": "Mobile App",
            "industry": "Health & Fitness"
        },
        {
            "name": "EventHub",
            "description": "An event management platform for planning, promoting, and managing events. It includes features for ticketing, attendee management, and event analytics.",
            "type": "Web & Mobile Application",
            "industry": "Event Management"
        }
    ],
    
    # Major projects
    "Projects": [
        {
            "name": "Banking Mobile App",
            "client": "Major Financial Institution",
            "description": "Developed a secure mobile banking application with features like account management, fund transfers, bill payments, and transaction history. The app includes biometric authentication for enhanced security.",
            "technologies": "React Native, Node.js, MongoDB, AWS"
        },
        {
            "name": "Healthcare Management System",
            "client": "Regional Hospital Network",
            "description": "Built a comprehensive healthcare management system for patient records, appointment scheduling, medical billing, and inventory management. The system improved operational efficiency by 40%.",
            "technologies": "Angular, Python, PostgreSQL, Docker"
        },
        {
            "name": "E-commerce Platform",
            "client": "Retail Chain",
            "description": "Created a full-featured e-commerce platform with product catalog, shopping cart, payment processing, order management, and customer relationship management. The platform increased online sales by 65%.",
            "technologies": "React, Django, MySQL, Redis"
        },
        {
            "name": "Real Estate Listing Portal",
            "client": "Property Management Company",
            "description": "Developed a property listing portal with search functionality, virtual tours, agent management, and lead generation. The portal includes interactive maps and neighborhood information.",
            "technologies": "Vue.js, Laravel, MongoDB, Google Maps API"
        },
        {
            "name": "Fleet Management System",
            "client": "Logistics Company",
            "description": "Built a system for tracking vehicles, managing drivers, optimizing delivery routes, and maintaining vehicle maintenance schedules. The system reduced fuel costs by 25% and improved delivery times.",
            "technologies": "React, Node.js, PostgreSQL, Google Maps API"
        },
        {
            "name": "Social Media Analytics Platform",
            "client": "Digital Marketing Agency",
            "description": "Developed a platform for tracking and analyzing social media performance across multiple platforms. The system provides insights on engagement, reach, and audience demographics.",
            "technologies": "Angular, Python, MongoDB, AWS"
        },
        {
            "name": "Inventory Management System",
            "client": "Manufacturing Company",
            "description": "Created a system for tracking inventory levels, managing suppliers, processing purchase orders, and generating reports. The system reduced inventory costs by 30%.",
            "technologies": "React, .NET Core, SQL Server"
        },
        {
            "name": "HR Management Portal",
            "client": "Corporate Enterprise",
            "description": "Built a portal for employee onboarding, attendance tracking, performance evaluation, and payroll management. The portal streamlined HR processes and improved employee satisfaction.",
            "technologies": "Vue.js, Spring Boot, PostgreSQL"
        },
        {
            "name": "Educational Learning Platform",
            "client": "University System",
            "description": "Developed an online learning platform with course management, virtual classrooms, assignment submission, and progress tracking. The platform enabled remote learning for over 50,000 students.",
            "technologies": "React, Node.js, MongoDB, WebRTC"
        },
        {
            "name": "IoT-based Smart Home Solution",
            "client": "Home Automation Company",
            "description": "Created a system for controlling and monitoring smart home devices through a mobile app. The solution includes energy usage tracking and automated routines.",
            "technologies": "Flutter, Python, MQTT, AWS IoT"
        }
    ],
    
    # Services offered
    "Services": [
        "Mobile App Development",
        "Web Development",
        "UI/UX Design",
        "E-commerce Solutions",
        "Enterprise Software Development",
        "Cloud Solutions",
        "IoT Application Development",
        "AI and Machine Learning Solutions",
        "Digital Marketing",
        "Quality Assurance and Testing",
        "DevOps Services",
        "Blockchain Development",
        "AR/VR Development",
        "CRM and ERP Solutions",
        "IT Consulting"
    ],
    
    # Industries served
    "Industries": [
        "Healthcare",
        "Finance & Banking",
        "Retail & E-commerce",
        "Education",
        "Transportation & Logistics",
        "Real Estate",
        "Manufacturing",
        "Travel & Hospitality",
        "Food & Beverage",
        "Media & Entertainment"
    ]
}

def get_product_info(product_name):
    """Get information about a specific product"""
    for product in COMPANY_PRODUCTS["Products"]:
        if product_name.lower() in product["name"].lower():
            return product
    return None

def get_project_info(project_name):
    """Get information about a specific project"""
    for project in COMPANY_PRODUCTS["Projects"]:
        if project_name.lower() in project["name"].lower():
            return project
    return None

def get_all_products_summary():
    """Get a summary of all products"""
    return ", ".join([product["name"] for product in COMPANY_PRODUCTS["Products"]])

def get_all_projects_summary():
    """Get a summary of all projects"""
    return ", ".join([project["name"] for project in COMPANY_PRODUCTS["Projects"]])

def get_services_summary():
    """Get a summary of all services"""
    return ", ".join(COMPANY_PRODUCTS["Services"])

def get_industries_summary():
    """Get a summary of all industries served"""
    return ", ".join(COMPANY_PRODUCTS["Industries"])