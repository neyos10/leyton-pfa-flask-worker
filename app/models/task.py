from datetime import datetime, timezone

from app import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    file_location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    parameters = db.Column(db.JSON, nullable=True)

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending', 'in_progress', 'done', 'failed')",
            name="task_status_check",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "file_location": self.file_location,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "parameters": self.parameters,
        }
