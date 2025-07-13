from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from .models import Voter, Candidate, Position, Vote, County, Constituency, Ward
from .tokens import email_verification_token


def home(request):
    return render(request, 'home.html')

def register(request):
    counties = County.objects.all()
    constituencies = Constituency.objects.all()
    wards = Ward.objects.all()

    if request.method == 'POST':
        full_name = request.POST['full_name']
        id_number = request.POST['id_number']
        email = request.POST['email']
        county_id = request.POST['county']
        constituency_id = request.POST['constituency']
        ward_id = request.POST['ward']

        if Voter.objects.filter(id_number=id_number).exists():
            messages.error(request, 'ID already registered.')
        elif Voter.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            county = get_object_or_404(County, id=county_id)
            constituency = get_object_or_404(Constituency, id=constituency_id, county=county)
            ward = get_object_or_404(Ward, id=ward_id, constituency=constituency)

            voter = Voter.objects.create(
                full_name=full_name,
                id_number=id_number,
                email=email,
                is_verified=False,
                county=county,
                constituency=constituency,
                ward=ward
            )

            uid = urlsafe_base64_encode(force_bytes(voter.pk))
            token = email_verification_token.make_token(voter)
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )

            send_mail(
                'Confirm your Email - E-Voting System',
                f'Hello {full_name},\n\nClick the link below to verify your email:\n\n{verification_link}\n\nThank you,\nE-Voting Team',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )

            messages.success(request, 'Registered! Check your email to verify your account.')
            return redirect('login')

    return render(request, 'register.html', {
        'counties': counties,
        'constituencies': constituencies,
        'wards': wards,
    })


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        voter = Voter.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Voter.DoesNotExist):
        voter = None

    if voter and email_verification_token.check_token(voter, token):
        voter.is_verified = True
        voter.save()
        messages.success(request, 'Email verified successfully! You can now log in and vote.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('home')


def voter_login(request):
    if request.method == 'POST':
        id_number = request.POST['id_number']
        voter = Voter.objects.filter(id_number=id_number).first()

        if voter:
            request.session['voter_id'] = voter.id
            messages.success(request, f"Welcome, {voter.full_name}!")
            return redirect('vote')
        else:
            messages.error(request, "Invalid ID.")

    return render(request, 'login.html')


def voter_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('home')


def vote(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        messages.error(request, "You must log in to vote.")
        return redirect('login')

    voter = Voter.objects.filter(id=voter_id).first()
    if not voter:
        messages.error(request, "Voter not found.")
        return redirect('login')

    if not voter.is_verified:
        messages.warning(request, "Please verify your email before voting.")
        return redirect('home')

    national_positions = Position.objects.filter(is_national=True)
    county_positions = Position.objects.filter(is_national=False)

    if request.method == 'POST':
        if voter.has_voted:
            messages.error(request, "You have already voted.")
            return redirect('vote')

        all_positions = list(national_positions) + list(county_positions)
        for position in all_positions:
            candidate_id = request.POST.get(f'position_{position.id}')
            if candidate_id:
                candidate = Candidate.objects.get(id=candidate_id)
                Vote.objects.create(voter=voter, candidate=candidate)

        voter.has_voted = True
        voter.save()
        messages.success(request, "Your vote has been cast.")
        return redirect('vote')

    national_data = []
    for position in national_positions:
        candidates = Candidate.objects.filter(position=position)
        national_data.append({
            'id': position.id,
            'name': position.name,
            'candidates': candidates
        })

    county_data = []
    for position in county_positions:
        candidates = Candidate.objects.filter(
            position=position,
            county=voter.county
        )
        if candidates.exists():
            county_data.append({
                'id': position.id,
                'name': position.name,
                'candidates': candidates
            })


    if not national_data and not county_data:
        messages.warning(request, "No positions available for you to vote for. Please contact the admin.")

    return render(request, 'vote.html', {
        'voter_id': voter_id,
        'voter': voter,
        'national_positions': national_data,
        'county_positions': county_data
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def results(request):
    positions = Position.objects.all()
    data = []

    for position in positions:
        candidates = Candidate.objects.filter(position=position).annotate(total_votes=Count('votes'))
        total = sum(c.total_votes for c in candidates)

        results_list = []
        for candidate in candidates:
            percent = (candidate.total_votes / total * 100) if total > 0 else 0
            results_list.append({
                'name': candidate.name,
                'votes': candidate.total_votes,
                'percent': round(percent, 2)
            })

        data.append({
            'position': position.name,
            'candidates': results_list
        })

    return render(request, 'results.html', {'results': data})


@staff_member_required
def manage_voters(request):
    voters = Voter.objects.all()

    if request.method == 'POST':
        delete_id = request.POST.get('delete_id')
        if delete_id:
            Voter.objects.filter(id=delete_id).delete()
            messages.success(request, "Voter deleted successfully.")
            return redirect('manage_voters')

    return render(request, 'manage_voters.html', {'voters': voters})


# 🔌 API endpoints for AJAX region filtering
def get_constituencies(request, county_id):
    constituencies = Constituency.objects.filter(county_id=county_id).values('id', 'name')
    return JsonResponse(list(constituencies), safe=False)


def get_wards(request, constituency_id):
    wards = Ward.objects.filter(constituency_id=constituency_id).values('id', 'name')
    return JsonResponse(list(wards), safe=False)
