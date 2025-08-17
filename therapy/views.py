from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import AppointmentRequest, FAQ


def home(request):
    """Home page view"""
    return render(request, 'therapy/home.html')


def faq(request):
    """FAQ page view"""
    faqs = FAQ.objects.filter(is_active=True)
    context = {
        'faqs': faqs
    }
    return render(request, 'therapy/faq.html', context)

def scheduling(request):
    """Scheduling page view"""
    return render(request, 'therapy/scheduling.html')


def submit_appointment(request):
    """Handle appointment form submission"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            surname = request.POST.get('surname', '').strip()
            email = request.POST.get('email', '').strip()
            reason = request.POST.get('reason', '').strip()

            # Validate required fields
            if not all([name, surname, email, reason]):
                messages.error(request, 'All fields are required.')
                return redirect('therapy:scheduling')

            # Create appointment request
            appointment = AppointmentRequest.objects.create(
                name=name,
                surname=surname,
                email=email,
                reason=reason
            )

            # Send email notification (optional)
            try:
                send_mail(
                    subject=f'New Appointment Request from {name} {surname}',
                    message=f"""
                    New appointment request received:

                    Name: {name} {surname}
                    Email: {email}
                    Reason: {reason}

                    Please respond to the client at your earliest convenience.
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['anpinghsia@andiehsialmft.com'],  # Replace with actual email
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending failed: {e}")

            messages.success(request,
                             'Thank you for your submission! I will reach out to you soon to discuss scheduling.')
            return redirect('therapy:scheduling')

        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('therapy:scheduling')

    return redirect('therapy:scheduling')