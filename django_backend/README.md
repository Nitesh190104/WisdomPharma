# Wisdom Pharma - Django Backend (INT253 Curriculum Aligned)

A full-stack, enterprise-grade Pharmacy Management & E-Commerce Web Application converted from Laravel (PHP) to **Python & Django 5**.

This project is structured specifically to cover all **6 Units** and **Practicals** of the **INT253: Web Development in Python using Django** curriculum, while providing full dual functionality:
1. **Server-Side Rendered (SSR) Web Portal**: Built using Django Templates (DTL), Django Forms, CSRF security, Sessions & Cookies.
2. **Headless REST API Backend**: Built with Django REST Framework (DRF) & SimpleJWT to power the modern React (Vite) frontend.
3. **Django Admin Panel**: Comprehensive data management with ORM, filters, and role-based permissions.

---

## 📚 INT253 Syllabus Mapping

### **Unit I: Introduction to Django**
- **Project Structure**: Created `wisdom_pharma/` project directory with standard `manage.py`, `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`.
- **Modular App Architecture**: 12 modular Django apps inside `apps/`:
  - `apps/web`: SSR templates, views, forms, and session management.
  - `apps/authentication`: Custom User model, OTP email verification, registration, JWT & session auth.
  - `apps/medicines`: Drug catalog, pricing, inventory, prescription flags.
  - `apps/categories`: Product categories and hierarchy.
  - `apps/cart`: Shopping cart with many-to-many items.
  - `apps/orders`: Retail & wholesale ordering, return workflows.
  - `apps/prescriptions`: Doctor Rx uploads and admin review.
  - `apps/notifications`: Real-time user notifications.
  - `apps/chatbot`: AI pharmacy assistant powered by Google Gemini API.
  - `apps/admin_panel`: Custom business logic dashboard.
  - `apps/contact`: Customer support inquiries.
  - `apps/site_content`: Dynamic CMS content.

### **Unit II: Views and URLs**
- **View Logic & HTTP Methods**: GET, POST, PUT, DELETE handled cleanly using both standard function-based views (FBVs) and class-based views (CBVs / `APIView`).
- **URL Routing & Parameters**: Parameter mapping with type converters (`<int:pk>/`, `<str:key>/`) in `apps/web/urls.py` and `apps/medicines/urls.py`.
- **Error Handling**: Custom 404 (`handler404_view`) and 500 (`handler500_view`) error handling templates.

### **Unit III: Templates, Debugging and Testing**
- **Django Template Language (DTL)**: Extensive use of template tags (`{% block %}`, `{% for %}`, `{% if %}`, `{% url %}`, `{% csrf_token %}`).
- **Template Inheritance**: Base layout in `templates/web/base.html` extended by `home.html`, `medicines.html`, `medicine_detail.html`, `contact.html`, `login.html`, `register.html`, `profile.html`.
- **Testing in Django**: Unit and integration tests written in `apps/web/tests.py` using `django.test.TestCase` and `Client`.

### **Unit IV: Forms in Django**
- **Django Forms & ModelForms**: Defined in `apps/web/forms.py` (`ContactForm`, `LoginForm`, `RegisterForm`, `MedicineFilterForm`).
- **Data Validation**: Custom validation methods (`clean()`, `clean_message()`, password confirmation matching).
- **CSRF Security**: `{% csrf_token %}` enforced across all POST forms.
- **POST-Redirect-Get (PRG) Pattern**: Implemented in contact, login, and registration workflows to prevent duplicate submissions on refresh.

### **Unit V: Models, Migrations, ORM and Django Admin**
- **ORM & Relationships**:
  - `OneToOneField`: `Business -> User`, `Cart -> User`
  - `ForeignKey`: `Medicine -> Category`, `Order -> User`, `Prescription -> User`
  - `ManyToManyField`: `Cart -> CartItem`
  - `JSONField`: Order items snapshot, addresses, notification payloads.
- **Django Admin (`/admin/`)**: Registered all models with `ModelAdmin` classes, custom search fields, filters, list displays, and tabular inlines in `admin.py`.
- **Database Configuration**: Supports MongoDB Atlas via `djongo` or SQLite/PostgreSQL.

### **Unit VI: Cookies, Sessions, Users and Authentication**
- **Sessions**: Storing visitor counts and user state in `request.session`.
- **Cookies**: Storing `last_visited` timestamps and `recent_medicines` history in browser cookies via `response.set_cookie()`.
- **User Authentication**: Django's native `login(request, user)` and `logout(request)` in session views, alongside JWT tokens for the React app.

---

## 🚀 Setup & Run Instructions

### 1. Requirements
- Python 3.10+
- Virtual environment (`venv`)

### 2. Installation
```bash
cd django_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 5. Run the Server
```bash
python manage.py runserver
```

The application will be accessible at:
- **Web Portal (DTL Templates)**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **REST API Endpoints**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- **React Frontend**: [http://localhost:5173/](http://localhost:5173/)
