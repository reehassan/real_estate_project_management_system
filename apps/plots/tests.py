from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.projects.models import Project
from .models import Plot, PlotAuditLog

User = get_user_model()


class PlotModelTest(TestCase):
    """
    Tests for the Plot model.
    Covers: creation, unique_together constraint, status tracking, audit log.
    """

    # ── Setup ──────────────────────────────────────────────────────
    def setUp(self):
        """
        Creates a user, a project, and one base plot for all tests.
        """
        self.user = User.objects.create_user(
            username = 'teststaff',
            password = 'testpass123',
            role     = 'STAFF'
        )

        self.project = Project.objects.create(
            name         = 'Dreamland Phase 1',
            location     = 'Near Motorway',
            city         = 'Lahore',
            project_type = Project.ProjectType.RESIDENTIAL,
            start_date   = '2024-01-01',
        )

        self.plot = Plot.objects.create(
            project     = self.project,
            plot_number = 'A-1',
            category    = Plot.PlotCategory.RESIDENTIAL,
            status      = Plot.PlotStatus.AVAILABLE,
            area        = 5.00,
            area_unit   = Plot.SizeUnit.MARLA,
            price       = 2500000.00,
            created_by  = self.user,
            updated_by  = self.user,
        )

    # ── Test 1 — Basic Creation ────────────────────────────────────
    def test_plot_created_successfully(self):
        """
        A plot saved to DB can be fetched back with correct values.
        """
        fetched = Plot.objects.get(plot_number='A-1', project=self.project)

        self.assertEqual(fetched.plot_number, 'A-1')
        self.assertEqual(fetched.area, 5.00)
        self.assertEqual(fetched.status, 'AVAILABLE')
        self.assertEqual(fetched.project, self.project)
        self.assertFalse(fetched.is_deleted)

    # ── Test 2 — __str__ Output ────────────────────────────────────
    def test_str_returns_project_and_plot_number(self):
        """
        __str__ should include both project name and plot number.
        """
        expected = f"{self.project.name} — Plot {self.plot.plot_number}"
        self.assertEqual(str(self.plot), expected)

    # ──────────────────────────────────────────────────────────────
    # UNIQUE CONSTRAINT TESTS
    # ──────────────────────────────────────────────────────────────

    # ── Test 3 — Duplicate Plot Blocked ───────────────────────────
    def test_duplicate_plot_number_in_same_project_blocked(self):
        """
        unique_together on (project, plot_number) must block duplicates.
        Creating plot 'A-1' again in same project should raise IntegrityError.
        This is the core financial protection — no double-selling a plot.
        """
        with self.assertRaises(IntegrityError):
            Plot.objects.create(
                project     = self.project,
                plot_number = 'A-1',        # same as setUp plot — must fail
                category    = Plot.PlotCategory.RESIDENTIAL,
                status      = Plot.PlotStatus.AVAILABLE,
                area        = 5.00,
                area_unit   = Plot.SizeUnit.MARLA,
            )

    # ── Test 4 — Same Number In Different Project Allowed ─────────
    def test_same_plot_number_in_different_project_allowed(self):
        """
        Plot 'A-1' can exist in Project B even if it exists in Project A.
        The unique constraint is per-project, not globally unique.
        """
        second_project = Project.objects.create(
            name         = 'Dreamland Phase 2',
            location     = 'Near Ring Road',
            city         = 'Lahore',
            project_type = Project.ProjectType.RESIDENTIAL,
            start_date   = '2024-06-01',
        )

        # this must NOT raise any error
        second_plot = Plot.objects.create(
            project     = second_project,
            plot_number = 'A-1',            # same number, different project — allowed
            category    = Plot.PlotCategory.RESIDENTIAL,
            status      = Plot.PlotStatus.AVAILABLE,
            area        = 5.00,
            area_unit   = Plot.SizeUnit.MARLA,
        )

        self.assertEqual(second_plot.plot_number, 'A-1')
        self.assertEqual(second_plot.project, second_project)

    # ── Test 5 — Different Numbers In Same Project Allowed ────────
    def test_different_plot_numbers_in_same_project_allowed(self):
        """
        A project can have multiple plots with different numbers.
        This is the normal case — make sure it works.
        """
        plot_b = Plot.objects.create(
            project     = self.project,
            plot_number = 'A-2',            # different number — allowed
            category    = Plot.PlotCategory.RESIDENTIAL,
            status      = Plot.PlotStatus.AVAILABLE,
            area        = 7.00,
            area_unit   = Plot.SizeUnit.MARLA,
        )

        total_plots = Plot.objects.filter(project=self.project).count()

        self.assertEqual(plot_b.plot_number, 'A-2')
        self.assertEqual(total_plots, 2)    # A-1 and A-2 both exist

    # ──────────────────────────────────────────────────────────────
    # STATUS TRACKING TESTS
    # ──────────────────────────────────────────────────────────────

    # ── Test 6 — Default Status Is Available ──────────────────────
    def test_default_status_is_available(self):
        """
        A new plot should default to AVAILABLE status.
        """
        new_plot = Plot.objects.create(
            project     = self.project,
            plot_number = 'B-1',
            category    = Plot.PlotCategory.COMMERCIAL,
            area        = 4.00,
            area_unit   = Plot.SizeUnit.MARLA,
        )

        self.assertEqual(new_plot.status, Plot.PlotStatus.AVAILABLE)

    # ── Test 7 — Status Transition Available → Booked ─────────────
    def test_status_changes_from_available_to_booked(self):
        """
        Plot status should update correctly when booking is made.
        This simulates the real workflow: plot gets booked by customer.
        """
        self.assertEqual(self.plot.status, 'AVAILABLE')

        self.plot.status = Plot.PlotStatus.BOOKED
        self.plot.save()

        # refresh_from_db fetches the latest value from DB
        # without this, self.plot might still show old value from memory
        self.plot.refresh_from_db()

        self.assertEqual(self.plot.status, 'BOOKED')

    # ── Test 8 — Status Transition Booked → Sold ──────────────────
    def test_status_changes_from_booked_to_sold(self):
        """
        Plot should move from BOOKED to SOLD after full payment.
        """
        self.plot.status = Plot.PlotStatus.BOOKED
        self.plot.save()

        self.plot.status = Plot.PlotStatus.SOLD
        self.plot.save()

        self.plot.refresh_from_db()

        self.assertEqual(self.plot.status, 'SOLD')

    # ── Test 9 — All Status Choices Save Correctly ────────────────
    def test_all_status_choices_are_valid(self):
        """
        Every status value must be saveable to the database.
        Tests that no status choice is misspelled or broken.
        """
        all_statuses = [
            Plot.PlotStatus.AVAILABLE,
            Plot.PlotStatus.BOOKED,
            Plot.PlotStatus.SOLD,
            Plot.PlotStatus.RESERVED,
        ]

        for status in all_statuses:
            self.plot.status = status
            self.plot.save()
            self.plot.refresh_from_db()
            self.assertEqual(self.plot.status, status)

    # ── Test 10 — Soft Delete Works ───────────────────────────────
    def test_soft_delete_preserves_record(self):
        """
        Soft deleting a plot sets is_deleted=True.
        The plot still exists in DB — data is never lost.
        """
        self.plot.is_deleted = True
        self.plot.save()

        still_exists = Plot.objects.filter(
            id = self.plot.id
        ).exists()

        self.assertTrue(still_exists)
        self.assertTrue(self.plot.is_deleted)

    # ── Test 11 — Price Is Optional ───────────────────────────────
    def test_plot_can_be_created_without_price(self):
        """
        Price is null=True in the model — should not be required.
        Plots are often registered before pricing is set.
        """
        plot_no_price = Plot.objects.create(
            project     = self.project,
            plot_number = 'C-1',
            category    = Plot.PlotCategory.RESIDENTIAL,
            area        = 5.00,
            area_unit   = Plot.SizeUnit.MARLA,
            price       = None,             # explicitly null
        )

        self.assertIsNone(plot_no_price.price)

    # ── Test 12 — Corner Flag ─────────────────────────────────────
    def test_corner_plot_flag(self):
        """
        is_corner defaults to False.
        Can be set to True for premium corner plots.
        """
        self.assertFalse(self.plot.is_corner)

        self.plot.is_corner = True
        self.plot.save()
        self.plot.refresh_from_db()

        self.assertTrue(self.plot.is_corner)


# ─────────────────────────────────────────────────────────────────
class PlotAuditLogTest(TestCase):
    """
    Tests for the PlotAuditLog model.
    Covers: log creation, action types, immutability logic.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username = 'auditor',
            password = 'testpass123',
            role     = 'OWNER'
        )

        self.project = Project.objects.create(
            name         = 'Test Project',
            location     = 'Test Location',
            city         = 'Islamabad',
            project_type = Project.ProjectType.RESIDENTIAL,
            start_date   = '2024-01-01',
        )

        self.plot = Plot.objects.create(
            project     = self.project,
            plot_number = 'X-1',
            category    = Plot.PlotCategory.RESIDENTIAL,
            area        = 5.00,
            area_unit   = Plot.SizeUnit.MARLA,
        )

    # ── Test 13 — Audit Log Created ───────────────────────────────
    def test_audit_log_can_be_created(self):
        """
        An audit log entry can be created and linked to a plot.
        """
        log = PlotAuditLog.objects.create(
            plot       = self.plot,
            action     = PlotAuditLog.Action.CREATED,
            changed_by = self.user,
            note       = 'Created during testing'
        )

        self.assertEqual(log.plot, self.plot)
        self.assertEqual(log.action, 'CREATED')
        self.assertEqual(log.changed_by, self.user)

    # ── Test 14 — Update Log Records Old And New Values ───────────
    def test_audit_log_records_field_change(self):
        """
        When a field changes, the audit log should store
        which field changed, what it was, and what it became.
        """
        log = PlotAuditLog.objects.create(
            plot       = self.plot,
            action     = PlotAuditLog.Action.UPDATED,
            changed_by = self.user,
            field_name = 'status',
            old_value  = 'AVAILABLE',
            new_value  = 'BOOKED',
        )

        self.assertEqual(log.field_name, 'status')
        self.assertEqual(log.old_value,  'AVAILABLE')
        self.assertEqual(log.new_value,  'BOOKED')

    # ── Test 15 — Multiple Logs Per Plot ──────────────────────────
    def test_plot_can_have_multiple_audit_logs(self):
        """
        A plot accumulates one log entry per change.
        All entries are retrievable through the related_name.
        """
        PlotAuditLog.objects.create(
            plot=self.plot, action=PlotAuditLog.Action.CREATED,
            changed_by=self.user
        )
        PlotAuditLog.objects.create(
            plot=self.plot, action=PlotAuditLog.Action.UPDATED,
            changed_by=self.user, field_name='status',
            old_value='AVAILABLE', new_value='BOOKED'
        )
        PlotAuditLog.objects.create(
            plot=self.plot, action=PlotAuditLog.Action.UPDATED,
            changed_by=self.user, field_name='price',
            old_value='2500000', new_value='3000000'
        )

        # access via related_name='audit_logs' on Plot model
        log_count = self.plot.audit_logs.count()

        self.assertEqual(log_count, 3)

    # ── Test 16 — Audit Log __str__ ───────────────────────────────
    def test_audit_log_str_contains_key_info(self):
        """
        __str__ of audit log should include plot, action, and user.
        """
        log = PlotAuditLog.objects.create(
            plot       = self.plot,
            action     = PlotAuditLog.Action.DELETED,
            changed_by = self.user,
        )

        log_str = str(log)

        # check all important parts are present
        self.assertIn('X-1',    log_str)    # plot number
        self.assertIn('DELETED', log_str)   # action
        self.assertIn('auditor', log_str)   # username

    # ── Test 17 — Changed At Auto Set ─────────────────────────────
    def test_changed_at_auto_set_on_creation(self):
        """
        changed_at is auto_now_add — must be set automatically.
        Should never be None.
        """
        log = PlotAuditLog.objects.create(
            plot       = self.plot,
            action     = PlotAuditLog.Action.CREATED,
            changed_by = self.user,
        )

        self.assertIsNotNone(log.changed_at)

    # ── Test 18 — Logs Ordered Newest First ───────────────────────
    def test_audit_logs_ordered_newest_first(self):
        """
        class Meta ordering = ['-changed_at'] means newest log
        should appear first when fetching all logs.
        """
        log1 = PlotAuditLog.objects.create(
            plot=self.plot, action=PlotAuditLog.Action.CREATED,
            changed_by=self.user
        )
        log2 = PlotAuditLog.objects.create(
            plot=self.plot, action=PlotAuditLog.Action.UPDATED,
            changed_by=self.user, field_name='status',
            old_value='AVAILABLE', new_value='BOOKED'
        )

        logs = PlotAuditLog.objects.filter(plot=self.plot)

        # first in queryset should be the most recently created
        self.assertEqual(logs.first(), log2)
        self.assertEqual(logs.last(),  log1)