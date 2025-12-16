from django.core.management.base import BaseCommand
from jobs.models import Category


class Command(BaseCommand):
    help = 'Add default categories to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing categories before adding new ones',
        )

    def handle(self, *args, **options):
        # Default categories with colors
        categories_data = [
            {'name': 'IT', 'color': '#667eea'},
            {'name': 'Finance', 'color': '#48bb78'},
            {'name': 'Healthcare', 'color': '#ed8936'},
            {'name': 'Education', 'color': '#9f7aea'},
            {'name': 'Marketing', 'color': '#f56565'},
            {'name': 'Sales', 'color': '#4299e1'},
            {'name': 'HR', 'color': '#38b2ac'},
            {'name': 'Engineering', 'color': '#805ad5'},
            {'name': 'Design', 'color': '#d69e2e'},
            {'name': 'Legal', 'color': '#4a5568'},
            {'name': 'Consulting', 'color': '#c05621'},
            {'name': 'Retail', 'color': '#e53e3e'},
            {'name': 'Manufacturing', 'color': '#2d3748'},
            {'name': 'Hospitality', 'color': '#c53030'},
            {'name': 'Media', 'color': '#744210'},
        ]

        if options['clear']:
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('All existing categories have been deleted.'))

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'color': cat_data['color']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                # Update color if category exists but color is different
                if category.color != cat_data['color']:
                    category.color = cat_data['color']
                    category.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'Updated color for category: {category.name}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Category already exists: {category.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {created_count} created, {updated_count} updated, '
            f'{len(categories_data) - created_count - updated_count} already exist'
        ))

