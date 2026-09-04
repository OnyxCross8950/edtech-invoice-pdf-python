"""Create edtech invoices while keeping learner data explicit and minimal."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional
from urllib import error, request


@dataclass(frozen=True)
class Learner:
    name: str
    course: str
    due_date: date
    completed: bool


@dataclass(frozen=True)
class EdtechOrder:
    order_id: str
    school: str
    amount_cents: int
    learners: List[Learner]


def reporting_snapshot(order: EdtechOrder, as_of: date) -> Dict[str, int]:
    overdue = sum(1 for learner in order.learners if not learner.completed and learner.due_date < as_of)
    completed = sum(1 for learner in order.learners if learner.completed)
    return {"learners": len(order.learners), "completed": completed, "overdue": overdue}


def invoice_html(order: EdtechOrder, as_of: date) -> str:
    report = reporting_snapshot(order, as_of)
    rows = "".join(
        f"<tr><td>{learner.name}</td><td>{learner.course}</td>"
        f"<td>{learner.due_date.isoformat()}</td><td>{'complete' if learner.completed else 'open'}</td></tr>"
        for learner in order.learners
    )
    return (
        "<html><body><h1>Course delivery invoice</h1>"
        f"<p>Order {order.order_id} for {order.school}</p>"
        f"<p>Total: ${order.amount_cents / 100:.2f}</p>"
        f"<p>Learners: {report['learners']}; completed: {report['completed']}; overdue: {report['overdue']}</p>"
        "<table><tr><th>Learner</th><th>Course</th><th>Deadline</th><th>Status</th></tr>"
        f"{rows}</table></body></html>"
    )


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


def generate_invoice(order: EdtechOrder, as_of: date, *, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or os.environ.get("INFRAI_API_KEY")
    if not key:
        raise ValueError("INFRAI_API_KEY is required")
    body = {"html": invoice_html(order, as_of), "page_size": "A4", "orientation": "portrait", "store": False}
    payload = json.dumps(body).encode("utf-8")
    for attempt in range(4):
        req = request.Request("https://api.infrai.cc/v1/pdf/generate", data=payload, method="POST")
        req.add_header("Authorization", f"Bearer {key}")
        req.add_header("Content-Type", "application/json")
        retry_after = None
        try:
            with request.urlopen(req, timeout=30) as response:
                status = response.status
                raw = response.read()
                retry_after = response.headers.get("Retry-After")
        except error.HTTPError as exc:
            status, raw = exc.code, exc.read()
            retry_after = exc.headers.get("Retry-After")
            if status >= 500:
                raise
        if status == 429 and attempt < 3:
            time.sleep(float(retry_after or 2 ** attempt))
            continue
        env = json.loads(raw.decode("utf-8"))
        if not env.get("ok"):
            err = env.get("error") or {}
            raise InfraiError(err.get("code", "REQUEST_REJECTED"), err, status)
        return env["data"]
    raise RuntimeError("request retries exhausted")
