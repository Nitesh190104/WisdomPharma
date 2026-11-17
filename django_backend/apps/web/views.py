from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseServerError

from apps.medicines.models import Medicine
from apps.categories.models import Category
from apps.orders.models import Order
from apps.authentication.models import User
from .forms import ContactForm, LoginForm, RegisterForm, MedicineFilterForm

# Unit II & III: Home view with dynamic context and template rendering
def home_view(request):
    featured_medicines = Medicine.objects.filter(is_active=True, stock__gt=0)[:8]
    categories = Category.objects.filter(is_active=True)[:6]

    # Unit VI: Session tracking for visitor counter
    visit_count = request.session.get('visit_count', 0) + 1
    request.session['visit_count'] = visit_count

    context = {
        'featured_medicines': featured_medicines,
        'categories': categories,
        'visit_count': visit_count,
        'page_title': 'Wisdom Pharma - Modern Pharmacy',
    }
    response = render(request, 'web/home.html', context)
    
    # Unit VI: Cookie demonstration
    if 'last_visited' not in request.COOKIES:
        from django.utils import timezone
        response.set_cookie('last_visited', timezone.now().strftime('%Y-%m-%d %H:%M:%S'), max_age=86400 * 7)
    return response

# Unit II & IV: Medicine list view with filtering & form handling
def medicine_list_view(request):
    form = MedicineFilterForm(request.GET)
    medicines = Medicine.objects.filter(is_active=True)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        in_stock = form.cleaned_data.get('in_stock')

        if search:
            medicines = medicines.filter(medicine_name__icontains=search)
        if min_price is not None:
            medicines = medicines.filter(retail_price__gte=min_price)
        if max_price is not None:
            medicines = medicines.filter(retail_price__lte=max_price)
        if in_stock:
            medicines = medicines.filter(stock__gt=0)

    categories = Category.objects.filter(is_active=True)
    return render(request, 'web/medicines.html', {
        'medicines': medicines,
        'categories': categories,
        'form': form,
    })

# Unit II: URL with parameters
def medicine_detail_view(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    
    # Unit VI: Track recently viewed medicines in cookies
    recent_ids = request.COOKIES.get('recent_medicines', '').split(',')
    recent_ids = [i for i in recent_ids if i and i != str(pk)]
    recent_ids.insert(0, str(pk))
    recent_ids = recent_ids[:5]

    response = render(request, 'web/medicine_detail.html', {'medicine': medicine})
    response.set_cookie('recent_medicines', ','.join(recent_ids), max_age=86400 * 30)
    return response

# Unit IV: Form validation & POST-Redirect-Get pattern
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_mail(
                subject=f"[Contact Form] {subject} from {name}",
                message=f"From: {name} <{email}>\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, 'Thank you! Your message has been sent successfully.')
            return redirect('web_contact')  # POST-Redirect-Get pattern
    else:
        form = ContactForm()

    return render(request, 'web/contact.html', {'form': form})

# Unit VI: Authentication, Session login and logout
def login_view(request):
    if request.user.is_authenticated:
        return redirect('web_home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)  # Django session login (Unit VI)
                    messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                    next_url = request.GET.get('next', 'web_home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account has been deactivated.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'web/login.html', {'form': form})

def logout_view(request):
    logout(request)  # Unit VI: Django logout
    messages.info(request, 'You have been logged out.')
    return redirect('web_home')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('web_home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.set_password(form.cleaned_data['password'])
            user.is_approved = (user.role == 'consumer')
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('web_login')
    else:
        form = RegisterForm()

    return render(request, 'web/register.html', {'form': form})

@login_required(login_url='web_login')
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'web/profile.html', {
        'user': request.user,
        'orders': orders,
    })

# Unit II: Error Handling
def handler404_view(request, exception=None):
    return render(request, 'web/404.html', status=404)

def handler500_view(request):
    return render(request, 'web/500.html', status=500)
