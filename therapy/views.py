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
            phone = request.POST.get('phone', '').strip()
            preferred_contact = request.POST.get('preferred_contact', '').strip()
            consent = request.POST.get('consent', '').strip()

            # Validate required fields
            if not all([name, surname, email, reason]):
                messages.error(request, 'All fields are required.')
                return redirect('therapy:scheduling')

            if not consent:
                messages.error(request, 'Please check the box to agree to the privacy policy.')
                return redirect('therapy:scheduling')

            # Validate email format
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('therapy:scheduling')

            # Create appointment request
            appointment = AppointmentRequest.objects.create(
                name=name,
                surname=surname,
                email=email,
                reason=reason
            )

            # Send email notification to therapist
            try:
                # Email to therapist
                therapist_subject = f'New Appointment Request from {name} {surname}'
                therapist_message = f"""
NOTICE: This communication may contain sensitive information. Please handle securely.

New appointment request received:

Name: {name} {surname}
Email: {email}
Reason for appointment: {reason}

Submission Date: {appointment.created_at.strftime('%B %d, %Y at %I:%M %p')}

Please respond to the client at your earliest convenience.

---
This is an automated message from your website contact form.
                """

                send_mail(
                    subject=therapist_subject,
                    message=therapist_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['Andie.hsia.lmft@gmail.com'],
                    fail_silently=False,
                )

                # Optional: Send confirmation email to client
                client_subject = 'Appointment Request Received - Andie Hsia, LMFT'
                client_message = f"""
Dear {name},

Thank you for your interest in therapy services. I have received your appointment request and will respond within 24-48 hours to discuss scheduling and next steps.

IMPORTANT PRIVACY NOTICE: Please do not reply to this email with sensitive health information. We will discuss confidential matters during our scheduled consultation.

If you have any urgent concerns, please contact me directly at [phone number] or seek immediate assistance from your healthcare provider or emergency services if needed.

Best regards,
Andie Hsia, LMFT

---
This is an automated confirmation message.
                """

                send_mail(
                    subject=client_subject,
                    message=client_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,  # Don't fail if client email fails
                )

            except Exception as e:
                print(f"Email sending failed: {e}")
                # Still show success to user even if email fails
                messages.warning(request,
                    'Your appointment request was saved, but there was an issue sending the notification email. '
                    'I will still receive your request and respond soon.')
                return redirect('therapy:scheduling')

            messages.success(request,
                             'Thank you for your submission! I will reach out to you within 24-48 hours to discuss scheduling.')
            return redirect('therapy:scheduling')

        except Exception as e:
            print(f"Error in submit_appointment: {e}")
            messages.error(request, 'An error occurred while processing your request. Please try again or contact me directly.')
            return redirect('therapy:scheduling')

    return redirect('therapy:scheduling')