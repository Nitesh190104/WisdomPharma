import os
import sys
import django
import urllib.parse
import json
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_pharma.settings')
django.setup()

from apps.categories.models import Category
from apps.medicines.models import Medicine
from apps.authentication.models import User, Business
from apps.site_content.models import SiteContent

raw_medicines = [
    # Table 1
    {
        'name': 'Paracetamol 500mg',
        'category': 'Tablet',
        'manufacturer': 'Cipla',
        'stock': 500,
        'retail_price': 30.0,
        'wholesale_price': 22.0,
        'gst': 12,
        'expiry_date': '2027-12-31',
        'min_wholesale_qty': 50,
        'description': 'Fever and pain relief',
        'composition': 'Paracetamol 500mg',
        'dosage': '1 tablet after meal',
        'prescription_required': False
    },
    {
        'name': 'Crocin Advance',
        'category': 'Tablet',
        'manufacturer': 'GSK',
        'stock': 400,
        'retail_price': 35.0,
        'wholesale_price': 26.0,
        'gst': 12,
        'expiry_date': '2027-11-30',
        'min_wholesale_qty': 50,
        'description': 'Used for headache and fever',
        'composition': 'Paracetamol 500mg',
        'dosage': '1 tablet twice daily',
        'prescription_required': False
    },
    {
        'name': 'Dolo 650',
        'category': 'Tablet',
        'manufacturer': 'Micro Labs',
        'stock': 600,
        'retail_price': 35.0,
        'wholesale_price': 28.0,
        'gst': 12,
        'expiry_date': '2027-10-31',
        'min_wholesale_qty': 50,
        'description': 'Pain and fever reducer',
        'composition': 'Paracetamol 650mg',
        'dosage': '1 tablet when needed',
        'prescription_required': False
    },
    {
        'name': 'Azithromycin 500',
        'category': 'Antibiotic',
        'manufacturer': 'Sun Pharma',
        'stock': 200,
        'retail_price': 120.0,
        'wholesale_price': 95.0,
        'gst': 12,
        'expiry_date': '2027-09-30',
        'min_wholesale_qty': 20,
        'description': 'Treats bacterial infections',
        'composition': 'Azithromycin 500mg',
        'dosage': '1 tablet once daily',
        'prescription_required': True
    },
    {
        'name': 'Amoxicillin 500',
        'category': 'Antibiotic',
        'manufacturer': 'Alkem',
        'stock': 250,
        'retail_price': 85.0,
        'wholesale_price': 65.0,
        'gst': 12,
        'expiry_date': '2027-08-31',
        'min_wholesale_qty': 30,
        'description': 'Antibiotic for bacterial infections',
        'composition': 'Amoxicillin 500mg',
        'dosage': '1 capsule twice daily',
        'prescription_required': True
    },
    {
        'name': 'Pantoprazole 40',
        'category': 'Tablet',
        'manufacturer': 'Aristo',
        'stock': 350,
        'retail_price': 90.0,
        'wholesale_price': 70.0,
        'gst': 12,
        'expiry_date': '2027-07-31',
        'min_wholesale_qty': 40,
        'description': 'Reduces stomach acid',
        'composition': 'Pantoprazole 40mg',
        'dosage': '1 tablet before breakfast',
        'prescription_required': False
    },
    {
        'name': 'Cetirizine 10mg',
        'category': 'Tablet',
        'manufacturer': 'Dr Reddy',
        'stock': 450,
        'retail_price': 25.0,
        'wholesale_price': 18.0,
        'gst': 12,
        'expiry_date': '2027-06-30',
        'min_wholesale_qty': 50,
        'description': 'Allergy and cold relief',
        'composition': 'Cetirizine 10mg',
        'dosage': '1 tablet at night',
        'prescription_required': False
    },
    {
        'name': 'Shelcal 500',
        'category': 'Tablet',
        'manufacturer': 'Torrent',
        'stock': 300,
        'retail_price': 110.0,
        'wholesale_price': 85.0,
        'gst': 12,
        'expiry_date': '2027-05-31',
        'min_wholesale_qty': 30,
        'description': 'Calcium supplement for bones',
        'composition': 'Calcium 500mg + Vitamin D3',
        'dosage': '1 tablet daily after meal',
        'prescription_required': False
    },
    {
        'name': 'Zincovit',
        'category': 'Tablet',
        'manufacturer': 'Apex Labs',
        'stock': 400,
        'retail_price': 105.0,
        'wholesale_price': 80.0,
        'gst': 12,
        'expiry_date': '2027-04-30',
        'min_wholesale_qty': 30,
        'description': 'Multivitamin with zinc',
        'composition': 'Multivitamins + Minerals + Zinc',
        'dosage': '1 tablet daily',
        'prescription_required': False
    },
    {
        'name': 'Evion 400',
        'category': 'Tablet',
        'manufacturer': 'P&G Health',
        'stock': 350,
        'retail_price': 40.0,
        'wholesale_price': 30.0,
        'gst': 12,
        'expiry_date': '2027-03-31',
        'min_wholesale_qty': 50,
        'description': 'Vitamin E supplement',
        'composition': 'Vitamin E 400mg',
        'dosage': '1 capsule daily',
        'prescription_required': False
    },
    {
        'name': 'Limcee 500',
        'category': 'Tablet',
        'manufacturer': 'Abbott',
        'stock': 500,
        'retail_price': 25.0,
        'wholesale_price': 18.0,
        'gst': 12,
        'expiry_date': '2027-02-28',
        'min_wholesale_qty': 50,
        'description': 'Vitamin C immunity booster',
        'composition': 'Vitamin C 500mg',
        'dosage': '1 chewable tablet daily',
        'prescription_required': False
    },
    {
        'name': 'Metformin 500',
        'category': 'Tablet',
        'manufacturer': 'USV',
        'stock': 300,
        'retail_price': 45.0,
        'wholesale_price': 32.0,
        'gst': 12,
        'expiry_date': '2027-01-31',
        'min_wholesale_qty': 40,
        'description': 'Controls blood sugar levels',
        'composition': 'Metformin 500mg',
        'dosage': '1 tablet twice daily with food',
        'prescription_required': True
    },
    {
        'name': 'Amlodipine 5mg',
        'category': 'Tablet',
        'manufacturer': 'Pfizer',
        'stock': 280,
        'retail_price': 50.0,
        'wholesale_price': 38.0,
        'gst': 12,
        'expiry_date': '2026-12-31',
        'min_wholesale_qty': 40,
        'description': 'Blood pressure management',
        'composition': 'Amlodipine 5mg',
        'dosage': '1 tablet in morning',
        'prescription_required': True
    },
    {
        'name': 'ORS Powder',
        'category': 'Syrup',
        'manufacturer': 'FDC',
        'stock': 600,
        'retail_price': 22.0,
        'wholesale_price': 16.0,
        'gst': 12,
        'expiry_date': '2027-08-31',
        'min_wholesale_qty': 50,
        'description': 'Oral rehydration salts',
        'composition': 'Electrolytes Powder',
        'dosage': 'Mix in 1 liter clean water',
        'prescription_required': False
    },
    {
        'name': 'Digene Gel',
        'category': 'Syrup',
        'manufacturer': 'Abbott',
        'stock': 200,
        'retail_price': 140.0,
        'wholesale_price': 110.0,
        'gst': 12,
        'expiry_date': '2027-05-31',
        'min_wholesale_qty': 20,
        'description': 'Acidity and gas relief syrup',
        'composition': 'Antacid Gel',
        'dosage': '2 teaspoons after meals',
        'prescription_required': False
    },
    {
        'name': 'Benadryl Syrup',
        'category': 'Syrup',
        'manufacturer': 'J&J',
        'stock': 220,
        'retail_price': 115.0,
        'wholesale_price': 90.0,
        'gst': 12,
        'expiry_date': '2027-04-30',
        'min_wholesale_qty': 20,
        'description': 'Cough and throat relief',
        'composition': 'Diphenhydramine Syrup',
        'dosage': '5ml when coughing',
        'prescription_required': False
    },
    {
        'name': 'Ascoril LS',
        'category': 'Syrup',
        'manufacturer': 'Glenmark',
        'stock': 180,
        'retail_price': 125.0,
        'wholesale_price': 98.0,
        'gst': 12,
        'expiry_date': '2027-03-31',
        'min_wholesale_qty': 20,
        'description': 'Productive wet cough syrup',
        'composition': 'Levosalbutamol + Ambroxol',
        'dosage': '5ml thrice daily',
        'prescription_required': True
    },
    {
        'name': 'Volini Spray',
        'category': 'Ointment',
        'manufacturer': 'Sun Pharma',
        'stock': 150,
        'retail_price': 160.0,
        'wholesale_price': 125.0,
        'gst': 12,
        'expiry_date': '2027-09-30',
        'min_wholesale_qty': 15,
        'description': 'Instant muscle pain spray',
        'composition': 'Diclofenac Spray',
        'dosage': 'Spray on affected area',
        'prescription_required': False
    },
    {
        'name': 'Vicks Vaporub',
        'category': 'Ointment',
        'manufacturer': 'P&G',
        'stock': 300,
        'retail_price': 60.0,
        'wholesale_price': 46.0,
        'gst': 12,
        'expiry_date': '2027-10-31',
        'min_wholesale_qty': 30,
        'description': 'Relief from cold and congestion',
        'composition': 'Menthol + Camphor + Eucalyptus',
        'dosage': 'Apply on chest and throat',
        'prescription_required': False
    },
    {
        'name': 'Otrivin Nasal Spray',
        'category': 'Ointment',
        'manufacturer': 'GSK',
        'stock': 160,
        'retail_price': 98.0,
        'wholesale_price': 78.0,
        'gst': 12,
        'expiry_date': '2027-06-30',
        'min_wholesale_qty': 20,
        'description': 'Fast blocked nose relief',
        'composition': 'Xylometazoline Spray',
        'dosage': '1 spray per nostril',
        'prescription_required': False
    },
    # Table 2
    {
        'name': 'Surgical Cotton 100g',
        'category': 'Surgical',
        'manufacturer': 'CarePlus',
        'stock': 250,
        'retail_price': 45.0,
        'wholesale_price': 32.0,
        'gst': 12,
        'expiry_date': '2029-01-31',
        'min_wholesale_qty': 50,
        'description': 'Absorbent medical cotton',
        'composition': 'Pure Cotton Roll',
        'dosage': 'For external dressing',
        'prescription_required': False
    },
    {
        'name': 'Band-Aid Strips',
        'category': 'Surgical',
        'manufacturer': 'J&J',
        'stock': 400,
        'retail_price': 50.0,
        'wholesale_price': 35.0,
        'gst': 12,
        'expiry_date': '2028-12-31',
        'min_wholesale_qty': 50,
        'description': 'Waterproof wound bandage',
        'composition': 'Adhesive Strips',
        'dosage': 'Single use for cuts',
        'prescription_required': False
    },
    {
        'name': 'Crepe Bandage 6cm',
        'category': 'Surgical',
        'manufacturer': 'Hansaplast',
        'stock': 180,
        'retail_price': 120.0,
        'wholesale_price': 90.0,
        'gst': 12,
        'expiry_date': '2029-03-31',
        'min_wholesale_qty': 20,
        'description': 'Elastic support bandage',
        'composition': 'Cotton Elastic Fabric',
        'dosage': 'Wrap firmly around sprain',
        'prescription_required': False
    },
    {
        'name': 'Gauze Roll',
        'category': 'Surgical',
        'manufacturer': 'MediWrap',
        'stock': 300,
        'retail_price': 30.0,
        'wholesale_price': 20.0,
        'gst': 12,
        'expiry_date': '2029-05-31',
        'min_wholesale_qty': 50,
        'description': 'Sterile wound dressing roll',
        'composition': 'Woven Cotton Gauze',
        'dosage': 'External dressing only',
        'prescription_required': False
    },
    {
        'name': 'Sterile Gloves',
        'category': 'Surgical',
        'manufacturer': 'Kapp Surgical',
        'stock': 350,
        'retail_price': 40.0,
        'wholesale_price': 26.0,
        'gst': 12,
        'expiry_date': '2028-08-31',
        'min_wholesale_qty': 50,
        'description': 'Latex examination gloves',
        'composition': 'Latex Examination Pair',
        'dosage': 'Disposable medical use',
        'prescription_required': False
    },
    {
        'name': 'Face Mask Pack',
        'category': 'Surgical',
        'manufacturer': 'ProtectCare',
        'stock': 500,
        'retail_price': 80.0,
        'wholesale_price': 50.0,
        'gst': 12,
        'expiry_date': '2029-06-30',
        'min_wholesale_qty': 50,
        'description': '3-ply medical surgical mask',
        'composition': 'Non-woven Fabric 3-ply',
        'dosage': 'Single use mask',
        'prescription_required': False
    },
    {
        'name': 'Hand Sanitizer 100ml',
        'category': 'Surgical',
        'manufacturer': 'Lifebuoy',
        'stock': 300,
        'retail_price': 50.0,
        'wholesale_price': 35.0,
        'gst': 18,
        'expiry_date': '2027-11-30',
        'min_wholesale_qty': 50,
        'description': '70% alcohol hand rub',
        'composition': 'Alcohol Gel 70%',
        'dosage': 'Apply on palms',
        'prescription_required': False
    },
    {
        'name': 'Syringe 5ml',
        'category': 'Surgical',
        'manufacturer': 'Dispovan',
        'stock': 800,
        'retail_price': 10.0,
        'wholesale_price': 6.0,
        'gst': 12,
        'expiry_date': '2029-04-30',
        'min_wholesale_qty': 100,
        'description': 'Single use sterile syringe',
        'composition': 'Plastic Syringe with Needle',
        'dosage': 'Clinical injection use',
        'prescription_required': False
    },
    {
        'name': 'Syringe 10ml',
        'category': 'Surgical',
        'manufacturer': 'Dispovan',
        'stock': 600,
        'retail_price': 15.0,
        'wholesale_price': 9.0,
        'gst': 12,
        'expiry_date': '2029-04-30',
        'min_wholesale_qty': 100,
        'description': 'Large volume sterile syringe',
        'composition': 'Plastic Syringe with Needle',
        'dosage': 'Clinical injection use',
        'prescription_required': False
    },
    {
        'name': 'Insulin Syringe',
        'category': 'Surgical',
        'manufacturer': 'BD Ultra-Fine',
        'stock': 400,
        'retail_price': 20.0,
        'wholesale_price': 14.0,
        'gst': 12,
        'expiry_date': '2029-02-28',
        'min_wholesale_qty': 50,
        'description': 'Fine needle for daily insulin',
        'composition': '31G Needle Syringe',
        'dosage': 'Subcutaneous injection',
        'prescription_required': False
    },
    {
        'name': 'Digital Thermometer',
        'category': 'Surgical',
        'manufacturer': 'Dr Trust',
        'stock': 120,
        'retail_price': 220.0,
        'wholesale_price': 170.0,
        'gst': 18,
        'expiry_date': '2030-12-31',
        'min_wholesale_qty': 10,
        'description': 'Accurate body temperature sensor',
        'composition': 'Electronic Sensor Device',
        'dosage': 'Oral or axillary reading',
        'prescription_required': False
    },
    {
        'name': 'Hot Water Bag',
        'category': 'Surgical',
        'manufacturer': 'Flamingo',
        'stock': 90,
        'retail_price': 280.0,
        'wholesale_price': 210.0,
        'gst': 12,
        'expiry_date': '2031-12-31',
        'min_wholesale_qty': 10,
        'description': 'Rubber heating bag for cramps',
        'composition': 'Vulcanized Rubber Bag',
        'dosage': 'Fill with warm water',
        'prescription_required': False
    },
    {
        'name': 'Nebulizer Mask Kit',
        'category': 'Surgical',
        'manufacturer': 'Omron',
        'stock': 110,
        'retail_price': 150.0,
        'wholesale_price': 110.0,
        'gst': 12,
        'expiry_date': '2029-09-30',
        'min_wholesale_qty': 10,
        'description': 'Adult aerosol nebulizer mask',
        'composition': 'Medical Grade PVC Kit',
        'dosage': 'Attach to nebulizer machine',
        'prescription_required': False
    },
    {
        'name': 'Adult Diapers',
        'category': 'Surgical',
        'manufacturer': 'Friends',
        'stock': 140,
        'retail_price': 450.0,
        'wholesale_price': 360.0,
        'gst': 12,
        'expiry_date': '2028-07-31',
        'min_wholesale_qty': 10,
        'description': 'Incontinence care diapers',
        'composition': 'Absorbent Polymer Briefs',
        'dosage': 'Wear as needed',
        'prescription_required': False
    },
    {
        'name': 'Urine Collection Bag',
        'category': 'Surgical',
        'manufacturer': 'Romsons',
        'stock': 200,
        'retail_price': 65.0,
        'wholesale_price': 45.0,
        'gst': 12,
        'expiry_date': '2029-05-31',
        'min_wholesale_qty': 30,
        'description': '2000ml sterile drainage bag',
        'composition': 'Graduated Plastic Drainage Bag',
        'dosage': 'Connect to catheter',
        'prescription_required': False
    },
    {
        'name': 'Pregnancy Test Kit',
        'category': 'Surgical',
        'manufacturer': 'Prega News',
        'stock': 300,
        'retail_price': 60.0,
        'wholesale_price': 42.0,
        'gst': 12,
        'expiry_date': '2027-12-31',
        'min_wholesale_qty': 50,
        'description': 'Home pregnancy test',
        'composition': 'HCG Detection Kit',
        'dosage': 'Single use',
        'prescription_required': False
    },
    {
        'name': 'Blood Glucose Strips',
        'category': 'Diabetes Care',
        'manufacturer': 'Accu-Chek',
        'stock': 150,
        'retail_price': 850.0,
        'wholesale_price': 760.0,
        'gst': 12,
        'expiry_date': '2028-05-31',
        'min_wholesale_qty': 10,
        'description': 'Sugar testing strips',
        'composition': 'Test Strips',
        'dosage': 'Use with glucometer',
        'prescription_required': False
    },
    {
        'name': 'Antiseptic Liquid 100ml',
        'category': 'First Aid',
        'manufacturer': 'Dettol',
        'stock': 320,
        'retail_price': 75.0,
        'wholesale_price': 58.0,
        'gst': 18,
        'expiry_date': '2028-11-30',
        'min_wholesale_qty': 50,
        'description': 'Kills germs on wounds',
        'composition': 'Chloroxylenol Solution',
        'dosage': 'External use',
        'prescription_required': False
    },
    {
        'name': 'Betadine Ointment',
        'category': 'First Aid',
        'manufacturer': 'Win-Medicare',
        'stock': 180,
        'retail_price': 95.0,
        'wholesale_price': 72.0,
        'gst': 12,
        'expiry_date': '2028-10-31',
        'min_wholesale_qty': 30,
        'description': 'Antiseptic wound cream',
        'composition': 'Povidone Iodine',
        'dosage': 'External use',
        'prescription_required': False
    },
    {
        'name': 'Micropore Tape',
        'category': 'Medical Supplies',
        'manufacturer': '3M',
        'stock': 250,
        'retail_price': 65.0,
        'wholesale_price': 48.0,
        'gst': 12,
        'expiry_date': '2029-02-28',
        'min_wholesale_qty': 50,
        'description': 'Medical adhesive tape',
        'composition': 'Paper Surgical Tape',
        'dosage': 'External use',
        'prescription_required': False
    }
]

def run():
    print("Clearing old categories and medicines...")
    Medicine.objects.all().delete()
    Category.objects.all().delete()

    cat_map = {}
    for m in raw_medicines:
        c_name = m['category']
        if c_name not in cat_map:
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', c_name).strip('-').lower()
            c, _ = Category.objects.get_or_create(
                name=c_name,
                defaults={
                    'slug': slug,
                    'description': f'Pharmaceutical products in {c_name} segment.',
                    'is_active': True,
                }
            )
            cat_map[c_name] = c

    app_url = 'http://localhost:8000'
    for med in raw_medicines:
        name = med['name']
        img_name = 'Antiseptic Liquid' if name == 'Antiseptic Liquid 100ml' else name
        quoted = urllib.parse.quote(img_name)
        image_url = f'{app_url}/images/medicines/{quoted}.avif'

        Medicine.objects.create(
            medicine_name=name,
            category=cat_map[med['category']],
            manufacturer=med['manufacturer'],
            stock=med['stock'],
            retail_price=med['retail_price'],
            wholesale_price=med['wholesale_price'],
            gst_percentage=med['gst'],
            expiry_date=med['expiry_date'],
            min_wholesale_qty=med['min_wholesale_qty'],
            description=med['description'],
            composition=med['composition'],
            dosage=med['dosage'],
            prescription_required=med['prescription_required'],
            image=image_url,
            is_active=True
        )

    print(f"Successfully seeded {Medicine.objects.count()} medicines across {Category.objects.count()} categories!")

    # Users
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'wisdom.admin@wisdompharma.com')
    admin_password = getattr(settings, 'ADMIN_PASSWORD', 'WisdomAdmin@123')
    if not User.objects.filter(email=admin_email).exists():
        admin_user = User.objects.create_superuser(
            email=admin_email,
            username=admin_email,
            password=admin_password,
            first_name='Wisdom',
            last_name='Admin',
            role='admin',
            is_approved=True,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        print(f"Admin user created: {admin_email} / {admin_password}")

    if not User.objects.filter(email='rahul@example.com').exists():
        User.objects.create_user(
            email='rahul@example.com',
            username='rahul@example.com',
            password='password123',
            first_name='Rahul',
            last_name='Sharma',
            role='consumer',
            phone='9876543210',
            address='123 MG Road',
            city='Varanasi',
            state='Uttar Pradesh',
            pincode='221006',
            is_approved=True
        )
        print("Consumer user created: rahul@example.com / password123")

    if not User.objects.filter(email='priya@medstore.com').exists():
        s = User.objects.create_user(
            email='priya@medstore.com',
            username='priya@medstore.com',
            password='password123',
            first_name='Priya',
            last_name='Patel',
            role='store',
            phone='9876543211',
            is_approved=True
        )
        Business.objects.create(
            user=s,
            business_name='Patel Medical Store',
            gst_number='27AABCU9603R1ZM',
            drug_license_number='UP-VAR-123456',
            is_verified=True
        )
        print("Store user created: priya@medstore.com / password123")

    # Seed About Page
    about_data = {
        'hero': {
            'tagline': '📍 Varanasi, Uttar Pradesh',
            'heading': 'About Wisdom Pharma',
            'subheading': "Varanasi's leading pharmaceutical wholesaler and distributor. Bridging manufacturers and healthcare centers with temperature-controlled, authentic, and fast distribution of life-saving medical supplies."
        },
        'mission': {
            'para1': 'Established as a premium pharmaceutical distributor in Varanasi, <strong>Wisdom Pharma</strong> serves both healthcare businesses (B2B) and individual consumers (B2C) by delivering authentic, high-efficacy pharmaceutical medications.',
            'para2': 'We specialize in distributing critical life-saving injections, specialty therapeutic tablets, premium surgical dressings (cotton gauze, wadding, bandages), and medical diagnostics equipment directly from verified manufacturers.',
            'para3': 'For over 5 years, our partners have trusted us for cold-chain shipping standards, competitive wholesale rates, absolute GST transparency, and verified logistical promptness across Uttar Pradesh and other regions.',
            'badge': '5+ Years of Trust',
            'badgeSub': 'IndiaMART Verified Distributor'
        },
        'banner': {
            'heading': 'Cold-Chain Approved & Authentic Supply Chain',
            'body': 'We store and ship our injections, insulin vials, and specialty tablets under rigorous cold-chain conditions. Rest assured of authentic medical supply logistics verified directly in Varanasi.',
            'pills': '✓ Genuine Drugs Only • ✓ GST Invoice Included • ✓ Prompt Local Logistics'
        },
        'specialties': [
            {'title': 'Critical & Life-Saving Injections', 'desc': 'Trusted supplier of high-demand critical injections including Bd Ampho, Xavitaz, Tigecycline, Streptokinase, Insulin, and Bd Dapto injections.', 'emoji': '💉', 'color': 'from-blue-500 to-indigo-500'},
            {'title': 'Specialty & Therapeutic Tablets', 'desc': 'Distributing essential oral therapeutic medications such as Posaconazole Gastro-Resistant tablets and Eplerenone tablets.', 'emoji': '💊', 'color': 'from-cyan-500 to-teal-500'},
            {'title': 'Medical Supplies & Dressing', 'desc': 'Providing high-quality clinical consumables like cotton gauze, premium cotton wadding, surgical bandages, and wound dressings.', 'emoji': '🩹', 'color': 'from-emerald-500 to-green-500'},
            {'title': 'Medical & Surgical Instruments', 'desc': 'Authorized wholesale vendor for medical instruments and precision surgical tools used in hospitals and diagnostic clinics.', 'emoji': '🔬', 'color': 'from-purple-500 to-pink-500'}
        ],
        'factsheet': [
            {'label': 'Nature of Business', 'value': 'Wholesaler, Distributor & Supplier', 'iconKey': 'HiOutlineOfficeBuilding'},
            {'label': 'Primary Location', 'value': 'Meera Nagar, Kandawa, Kanchanpur, Chitayipur, Varanasi - 221008', 'iconKey': 'HiOutlineLocationMarker'},
            {'label': 'Industry Presence', 'value': '5+ Years Verified Trust', 'iconKey': 'HiOutlineBadgeCheck'},
            {'label': 'Logistics Capability', 'value': 'Prompt UP & Pan-India Cold Chain Delivery', 'iconKey': 'HiOutlineTruck'},
            {'label': 'Quality Standard', 'value': '100% Genuine & Sourced Authentically', 'iconKey': 'HiOutlineShieldCheck'},
            {'label': 'Support Timeline', 'value': '24/7 Bulk Inquiry Response', 'iconKey': 'HiOutlineClock'}
        ]
    }

    content, _ = SiteContent.objects.get_or_create(key='about')
    content.value = json.dumps(about_data)
    content.save()
    print("About content successfully seeded!")

if __name__ == '__main__':
    run()
