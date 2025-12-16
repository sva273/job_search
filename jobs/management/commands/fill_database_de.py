from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from jobs.models import JobEntry, Category, Tag
import random


class Command(BaseCommand):
    help = 'Fill database with German IT job entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username to create jobs for (default: testuser)',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of job entries to create (default: 20)',
        )

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'password': 'pbkdf2_sha256$600000$dummy$dummy='  # Dummy password
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing user: {username}'))
        
        # Create IT category
        it_category, _ = Category.objects.get_or_create(
            name='IT',
            defaults={'color': '#667eea'}
        )
        
        # Create tags
        tags_data = [
            'Python', 'Django', 'JavaScript', 'React', 'Vue.js', 'Node.js',
            'Java', 'Spring', 'SQL', 'PostgreSQL', 'MongoDB', 'Docker',
            'Kubernetes', 'AWS', 'Azure', 'DevOps', 'Full Stack', 'Backend',
            'Frontend', 'Machine Learning', 'Data Science', 'Agile', 'Scrum'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        # German IT job titles
        job_titles = [
            'Softwareentwickler (m/w/d)',
            'Senior Python Entwickler',
            'Full Stack Developer',
            'Backend Entwickler',
            'Frontend Entwickler',
            'DevOps Engineer',
            'Cloud Architect',
            'Data Engineer',
            'Machine Learning Engineer',
            'Java Entwickler',
            'React Developer',
            'Django Entwickler',
            'System Administrator',
            'IT Projektmanager',
            'Software Architect',
            'QA Engineer',
            'Security Engineer',
            'Mobile App Entwickler',
            'Blockchain Entwickler',
            'AI Engineer'
        ]
        
        # German employers
        employers = [
            'SAP SE',
            'Siemens AG',
            'BMW Group',
            'Volkswagen AG',
            'Bosch',
            'Siemens Healthineers',
            'Zalando',
            'Delivery Hero',
            'HelloFresh',
            'Rocket Internet',
            'TeamViewer',
            'Trivago',
            'Auto1 Group',
            'About You',
            'Celonis',
            'Personio',
            'N26',
            'Trade Republic',
            'GetYourGuide',
            'Babbel'
        ]
        
        # German cities
        cities = [
            'Berlin', 'München', 'Hamburg', 'Frankfurt am Main', 'Köln',
            'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig',
            'Bremen', 'Dresden', 'Hannover', 'Nürnberg', 'Duisburg',
            'Bochum', 'Wuppertal', 'Bielefeld', 'Bonn', 'Münster'
        ]
        
        # Job descriptions in German
        descriptions = [
            'Wir suchen einen erfahrenen Softwareentwickler für unser innovatives Team. Sie werden an spannenden Projekten arbeiten und moderne Technologien einsetzen.',
            'Als Teil unseres Entwicklungsteams entwickeln Sie skalierbare Softwarelösungen und arbeiten mit modernen Frameworks und Tools.',
            'Sie sind verantwortlich für die Entwicklung und Wartung unserer Web-Anwendungen. Erfahrung mit agilen Methoden ist von Vorteil.',
            'In dieser Position entwickeln Sie Backend-Services und APIs. Sie arbeiten eng mit dem Frontend-Team zusammen.',
            'Wir bieten eine spannende Position in einem dynamischen Umfeld. Sie arbeiten an der Entwicklung neuer Features und der Optimierung bestehender Systeme.',
            'Als Full Stack Developer entwickeln Sie sowohl Frontend- als auch Backend-Komponenten unserer Anwendung.',
            'Sie unterstützen unser Team bei der Entwicklung cloud-basierter Lösungen und der Migration bestehender Systeme.',
            'In dieser Rolle arbeiten Sie an Data-Pipelines und Machine-Learning-Modellen. Erfahrung mit Python und Data-Science-Tools erforderlich.',
            'Wir suchen einen erfahrenen Entwickler für die Entwicklung und Wartung unserer Microservices-Architektur.',
            'Sie entwickeln mobile Anwendungen für iOS und Android. Erfahrung mit React Native oder Flutter ist wünschenswert.'
        ]
        
        # Sources
        sources = ['linkedin', 'indeed', 'company_website', 'recruiter', 'referral', 'other']
        
        # Work types
        work_types = ['remote', 'office', 'hybrid', 'flexible']
        
        # Priorities
        priorities = ['high', 'medium', 'low']
        
        # Statuses
        statuses = ['not_applied', 'applied', 'confirmed', 'response_received', 'rejected', 'accepted']
        
        # Create job entries
        created_count = 0
        for i in range(count):
            job_title = random.choice(job_titles)
            employer = random.choice(employers)
            city = random.choice(cities)
            
            # Random dates
            days_ago = random.randint(0, 180)
            created_date = timezone.now() - timedelta(days=days_ago)
            
            # Random status
            status = random.choice(statuses)
            
            # Create job entry
            job_entry = JobEntry.objects.create(
                user=user,
                job_title=job_title,
                employer=employer,
                address=f'{city}, Deutschland',
                contact_email=f'hr@{employer.lower().replace(" ", "").replace(".", "")}.de',
                contact_phone=f'+49 {random.randint(30, 89)} {random.randint(1000, 9999)} {random.randint(100, 999)}',
                company_website=f'https://www.{employer.lower().replace(" ", "").replace(".", "")}.de',
                job_url=f'https://www.{employer.lower().replace(" ", "").replace(".", "")}.de/karriere/{random.randint(1000, 9999)}',
                description=random.choice(descriptions),
                category=it_category,
                salary_min=random.randint(50000, 80000),
                salary_max=random.randint(80000, 120000),
                salary_currency='EUR',
                work_type=random.choice(work_types),
                priority=random.choice(priorities),
                source=random.choice(sources),
                status=status,
                created_at=created_date,
            )
            
            # Add random tags (2-5 tags per job)
            num_tags = random.randint(2, 5)
            selected_tags = random.sample(tags, min(num_tags, len(tags)))
            job_entry.tags.set(selected_tags)
            
            # Set dates based on status
            if status in ['applied', 'confirmed', 'response_received', 'rejected', 'accepted']:
                job_entry.resume_submitted = True
                job_entry.resume_submitted_date = created_date + timedelta(days=random.randint(1, 7))
            
            if status in ['confirmed', 'response_received', 'rejected', 'accepted']:
                job_entry.application_confirmed = True
                job_entry.confirmation_date = job_entry.resume_submitted_date + timedelta(days=random.randint(1, 5))
            
            if status in ['response_received', 'rejected', 'accepted']:
                job_entry.response_received = True
                job_entry.response_date = job_entry.confirmation_date + timedelta(days=random.randint(3, 14))
            
            if status == 'rejected':
                job_entry.rejection_received = True
                job_entry.rejection_date = job_entry.response_date + timedelta(days=random.randint(1, 3))
            
            # Add interview dates for some entries
            if status in ['confirmed', 'response_received', 'accepted']:
                if random.random() > 0.5:
                    job_entry.interview_date = timezone.now() + timedelta(days=random.randint(1, 30))
            
            # Add follow-up dates
            if status in ['applied', 'confirmed']:
                if random.random() > 0.6:
                    job_entry.follow_up_date = timezone.now() + timedelta(days=random.randint(1, 14))
            
            # Add application deadlines
            if random.random() > 0.7:
                job_entry.application_deadline = timezone.now().date() + timedelta(days=random.randint(1, 60))
            
            job_entry.save()
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} German IT job entries for user "{username}"'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Created category: {it_category.name}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Created {len(tags)} tags'
            )
        )

