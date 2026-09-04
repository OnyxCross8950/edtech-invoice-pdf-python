from datetime import date
from invoice_service import EdtechOrder, Learner, invoice_html, reporting_snapshot


def test_reporting_marks_only_past_open_deadlines_overdue():
    order = EdtechOrder("X", "School", 1000, [
        Learner("done", "Algebra", date(2026, 9, 1), True),
        Learner("late", "Algebra", date(2026, 9, 1), False),
        Learner("due", "Algebra", date(2026, 9, 2), False),
    ])
    assert reporting_snapshot(order, date(2026, 9, 2)) == {"learners": 3, "completed": 1, "overdue": 1}
    assert "overdue: 1" in invoice_html(order, date(2026, 9, 2))
