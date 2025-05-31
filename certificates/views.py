from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse
from django.conf import settings
from django.core.files.base import ContentFile

import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from PIL import Image
import qrcode
from io import BytesIO
from reportlab.lib.utils import ImageReader

from .models import Certificate, CertificateTemplate
from .forms import CertificateTemplateForm
from courses.models import Course, Enrollment

@login_required
def student_certificates(request):
    """Liste tous les certificats d'un étudiant"""
    certificates = Certificate.objects.filter(student=request.user).order_by('-issued_date')
    
    return render(request, 'certificates/student_certificates.html', {
        'certificates': certificates
    })

@login_required
def certificate_detail(request, certificate_id):
    """Affiche les détails d'un certificat"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    # Vérifier que l'utilisateur a le droit de voir ce certificat
    if certificate.student != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de voir ce certificat.")
    
    # Si le fichier PDF n'existe pas, le générer
    if not certificate.pdf_file:
        generate_certificate_pdf(certificate)
    
    return render(request, 'certificates/certificate_detail.html', {
        'certificate': certificate,
        'verification_url': request.build_absolute_uri(
            certificate.get_verification_url()
        )
    })

@login_required
def certificate_download(request, certificate_id):
    """Télécharger un certificat au format PDF"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    # Vérifier que l'utilisateur a le droit de télécharger ce certificat
    if certificate.student != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de télécharger ce certificat.")
    
    # Si le fichier PDF n'existe pas, le générer
    if not certificate.pdf_file:
        generate_certificate_pdf(certificate)
    
    # Renvoyer le fichier PDF
    response = FileResponse(
        certificate.pdf_file,
        as_attachment=True,
        filename=f'certificat_{certificate.certificate_id}.pdf'
    )
    return response

def certificate_verify(request, certificate_id):
    """Vérification publique de l'authenticité d'un certificat"""
    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)
        valid = certificate.is_valid
    except Certificate.DoesNotExist:
        certificate = None
        valid = False
    
    return render(request, 'certificates/certificate_verify.html', {
        'certificate': certificate,
        'valid': valid
    })

@login_required
def certificate_templates(request):
    """Liste tous les modèles de certificats (admin uniquement)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    templates = CertificateTemplate.objects.all().order_by('-created')
    
    return render(request, 'certificates/admin/certificate_templates.html', {
        'templates': templates
    })

@login_required
def create_certificate_template(request):
    """Créer un nouveau modèle de certificat (admin uniquement)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    if request.method == 'POST':
        form = CertificateTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save()
            messages.success(request, f"Le modèle '{template.name}' a été créé avec succès.")
            return redirect('certificate_templates')
    else:
        form = CertificateTemplateForm()
    
    return render(request, 'certificates/admin/create_certificate_template.html', {
        'form': form
    })

@login_required
def edit_certificate_template(request, template_id):
    """Modifier un modèle de certificat existant (admin uniquement)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    template = get_object_or_404(CertificateTemplate, id=template_id)
    
    if request.method == 'POST':
        form = CertificateTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, f"Le modèle '{template.name}' a été mis à jour avec succès.")
            return redirect('certificate_templates')
    else:
        form = CertificateTemplateForm(instance=template)
    
    return render(request, 'certificates/admin/edit_certificate_template.html', {
        'form': form,
        'template': template
    })

@login_required
def delete_certificate_template(request, template_id):
    """Supprimer un modèle de certificat (admin uniquement)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    template = get_object_or_404(CertificateTemplate, id=template_id)
    
    if request.method == 'POST':
        template.delete()
        messages.success(request, f"Le modèle '{template.name}' a été supprimé avec succès.")
        return redirect('certificate_templates')
    
    return render(request, 'certificates/admin/delete_certificate_template.html', {
        'template': template
    })

# Fonction utilitaire pour générer un certificat PDF
def generate_certificate_pdf(certificate):
    """Génère un certificat au format PDF"""
    # Récupérer le modèle par défaut ou le premier disponible
    template = CertificateTemplate.objects.filter(is_default=True).first()
    if not template:
        template = CertificateTemplate.objects.first()
    
    # Configurer le buffer pour le PDF
    buffer = BytesIO()
    
    # Créer un objet PDF avec ReportLab
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Si un fond d'image est disponible dans le modèle
    if template and template.background_image:
        img_path = os.path.join(settings.MEDIA_ROOT, template.background_image.name)
        p.drawImage(img_path, 0, 0, width, height)
    
    # Titre
    p.setFont("Helvetica-Bold", 24)
    title = template.title_text if template else "Certificat d'Accomplissement"
    p.drawCentredString(width/2, height-5*cm, title)
    
    # Corps du certificat
    p.setFont("Helvetica", 16)
    
    # Utilisez la template si disponible, sinon texte par défaut
    if template:
        # Remplacer les placeholders par les valeurs réelles
        body_text = template.body_text
        body_text = body_text.replace("{student_name}", f"{certificate.student.first_name} {certificate.student.last_name}")
        body_text = body_text.replace("{course_title}", certificate.course.title)
    else:
        body_text = f"Ce certificat est décerné à {certificate.student.first_name} {certificate.student.last_name} pour avoir complété avec succès le cours {certificate.course.title}."
    
    # Ajouter des sauts de ligne pour le texte long
    lines = [body_text[i:i+70] for i in range(0, len(body_text), 70)]
    y_pos = height/2
    for line in lines:
        p.drawCentredString(width/2, y_pos, line)
        y_pos -= cm
    
    # Date
    p.setFont("Helvetica-Oblique", 12)
    date_str = certificate.issued_date.strftime("%d %B %Y")
    p.drawCentredString(width/2, y_pos-2*cm, f"Date d'émission: {date_str}")
    
    # Identifiant unique du certificat
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, 2*cm, f"Identifiant: {certificate.certificate_id}")
    
    # Signature si disponible
    if template and template.signature_image:
        sig_path = os.path.join(settings.MEDIA_ROOT, template.signature_image.name)
        p.drawImage(sig_path, width/2-2.5*cm, 3*cm, 5*cm, 2*cm)
    
    # QR code pour la vérification
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Utilisez une URL relative pour la vérification, qui sera transformée en URL absolue lors de l'affichage
    verification_url = f"/certificates/verify/{certificate.certificate_id}/"
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    img.save(qr_buffer)
    qr_buffer.seek(0)
    
    p.drawImage(ImageReader(qr_buffer), 5*cm, 2*cm, 3*cm, 3*cm)
    
    p.save()
    
    # Enregistrer le PDF dans le fichier de certificat
    buffer.seek(0)
    certificate.pdf_file.save(f'certificat_{certificate.certificate_id}.pdf', ContentFile(buffer.getvalue()))
    certificate.save()
