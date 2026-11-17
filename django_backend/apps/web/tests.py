from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User
from apps.categories.models import Category
from apps.medicines.models import Medicine

class MedicineModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pain Relief', slug='pain-relief')
        self.medicine = Medicine.objects.create(
            medicine_name='Paracetamol 500mg',
            category=self.category,
            retail_price=20.0,
            wholesale_price=15.0,
            gst_percentage=12.0,
            stock=100,
            is_active=True
        )

    def test_medicine_creation(self):
        self.assertEqual(self.medicine.medicine_name, 'Paracetamol 500mg')
        self.assertEqual(self.medicine.stock, 100)
        self.assertTrue(self.medicine.is_active)

    def test_price_with_gst(self):
        # 20 + (20 * 0.12) = 22.40
        self.assertAlmostEqual(self.medicine.retail_price_with_gst(), 22.40, places=2)

class WebViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Antibiotics', slug='antibiotics')
        self.medicine = Medicine.objects.create(
            medicine_name='Amoxicillin 500mg',
            category=self.category,
            retail_price=50.0,
            stock=25,
            is_active=True
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse('web_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wisdom Pharma')

    def test_medicines_catalog_page(self):
        response = self.client.get(reverse('web_medicines'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amoxicillin 500mg')

    def test_contact_page_get(self):
        response = self.client.get(reverse('web_contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get in Touch')
