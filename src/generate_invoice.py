from datetime import date
from invoice_service import EdtechOrder, Learner, generate_invoice


if __name__ == "__main__":
    order = EdtechOrder(
        order_id="EDU-1042",
        school="Northside Learning",
        amount_cents=12500,
        learners=[Learner("A. Chen", "Clinical math", date(2026, 9, 15), False)],
    )
    print(generate_invoice(order, date(2026, 9, 2)))
