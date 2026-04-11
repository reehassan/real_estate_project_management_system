from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from .models import Project

User = get_user_model()


class ProjectModelTest(TestCase):
    """
    Tests for the Project model.
    Covers: creation, __str__, slug, soft delete, status.
    """

    # ── Setup — runs before every single test method ──────────────
    def setUp(self):
        """
        Creates reusable objects for all tests in this class.
        Called fresh before each test — tests never share state.
        """
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'testpass123',
            role     = 'STAFF'
        )

        self.project = Project.objects.create(
            name         = 'Dreamland Phase 1',
            location     = 'Near Motorway, Lahore',
            city         = 'Lahore',
            project_type = Project.ProjectType.RESIDENTIAL,
            status       = Project.ProjectStatus.ACTIVE,
            start_date   = '2024-01-01',
        )

    # ── Test 1 — Basic Creation ────────────────────────────────────
    def test_project_created_successfully(self):
        """
        A project saved to DB can be fetched back with correct values.
        """
        fetched = Project.objects.get(name='Dreamland Phase 1')

        self.assertEqual(fetched.name, 'Dreamland Phase 1')
        self.assertEqual(fetched.city, 'Lahore')
        self.assertEqual(fetched.project_type, 'RESIDENTIAL')
        self.assertEqual(fetched.status, 'ACTIVE')
        self.assertFalse(fetched.is_deleted)

    # ── Test 2 — __str__ Returns Name ─────────────────────────────
    def test_str_returns_project_name(self):
        """
        __str__ should return the project name.
        """
        self.assertEqual(str(self.project), 'Dreamland Phase 1')

    # ── Test 3 — Slug Auto Generation ─────────────────────────────
    def test_slug_auto_generated_from_name(self):
        """
        Slug should be auto-generated from name if not provided.
        'Dreamland Phase 1' → 'dreamland-phase-1'
        """
        expected_slug = slugify('Dreamland Phase 1')
        self.assertEqual(self.project.slug, expected_slug)

    # ── Test 4 — Slug Not Overwritten On Update ────────────────────
    def test_slug_not_overwritten_on_update(self):
        """
        Once a slug is set, updating the name should NOT change slug.
        URLs must stay stable — broken links are bad.
        """
        original_slug = self.project.slug

        self.project.name = 'Dreamland Phase 1 Updated'
        self.project.save()

        self.assertEqual(self.project.slug, original_slug)

    # ── Test 5 — Soft Delete ───────────────────────────────────────
    def test_soft_delete_sets_flag(self):
        """
        Soft deleting a project sets is_deleted=True.
        The record still exists in the database.
        """
        self.project.is_deleted = True
        self.project.save()

        # record still in DB
        still_exists = Project.objects.filter(
            name = 'Dreamland Phase 1'
        ).exists()

        self.assertTrue(still_exists)
        self.assertTrue(self.project.is_deleted)

    # ── Test 6 — Status Choices Are Valid ─────────────────────────
    def test_all_status_choices_are_valid(self):
        """
        Every status in ProjectStatus.choices should be saveable.
        """
        valid_statuses = [
            Project.ProjectStatus.PLANNING,
            Project.ProjectStatus.ACTIVE,
            Project.ProjectStatus.ON_HOLD,
            Project.ProjectStatus.COMPLETED,
            Project.ProjectStatus.CANCELLED,
        ]

        for status in valid_statuses:
            self.project.status = status
            self.project.save()
            self.project.refresh_from_db()
            self.assertEqual(self.project.status, status)

    # ── Test 7 — Default Status Is Planning ───────────────────────
    def test_default_status_is_planning(self):
        """
        A new project without explicit status defaults to PLANNING.
        """
        new_project = Project.objects.create(
            name         = 'New Project',
            location     = 'Test Location',
            city         = 'Karachi',
            project_type = Project.ProjectType.COMMERCIAL,
            start_date   = '2024-06-01',
        )

        self.assertEqual(new_project.status, Project.ProjectStatus.PLANNING)

    # ── Test 8 — Timestamps Auto Set ──────────────────────────────
    def test_created_at_and_updated_at_auto_set(self):
        """
        created_at and updated_at should be automatically set on save.
        """
        self.assertIsNotNone(self.project.created_at)
        self.assertIsNotNone(self.project.updated_at)

    # ── Test 9 — Project Type Choices ─────────────────────────────
    def test_project_type_choices(self):
        """
        All ProjectType choices should be saveable.
        """
        valid_types = [
            Project.ProjectType.RESIDENTIAL,
            Project.ProjectType.COMMERCIAL,
            Project.ProjectType.INDUSTRIAL,
            Project.ProjectType.AGRICULTURAL,
        ]

        for ptype in valid_types:
            self.project.project_type = ptype
            self.project.save()
            self.project.refresh_from_db()
            self.assertEqual(self.project.project_type, ptype)