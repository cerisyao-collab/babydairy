"""Record management service"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import Optional, List
import uuid

from src.models.record import Record, RECORD_TYPES
from src.models.user import User


# Default duplicate detection window in minutes
DEFAULT_DUPLICATE_WINDOW_MINUTES = 5


class RecordService:
    """Service for managing baby diary records"""

    def __init__(self, db: Session):
        self.db = db

    def create_record(
        self,
        user_id: str,
        record_type: str,
        details: dict,
        timestamp: Optional[str] = None,
        images: Optional[List[str]] = None,
        skip_duplicate_check: bool = False,
        duplicate_window_minutes: int = DEFAULT_DUPLICATE_WINDOW_MINUTES,
    ) -> Record:
        """
        Create a new record for a user

        Args:
            user_id: User's UUID
            record_type: Type of record (feeding, bowel, etc.)
            details: Record-specific details
            timestamp: ISO format timestamp, defaults to now
            images: List of image URLs/paths
            skip_duplicate_check: Skip duplicate detection
            duplicate_window_minutes: Window for duplicate detection

        Returns:
            Created Record object

        Raises:
            ValueError: If record type is invalid
            DuplicateRecordError: If similar record exists in time window
        """
        # Validate record type
        if record_type not in RECORD_TYPES:
            raise ValueError(f"Invalid record type: {record_type}. Must be one of {RECORD_TYPES}")

        # Parse timestamp
        if timestamp is None:
            ts = datetime.utcnow()
        else:
            ts = datetime.fromisoformat(timestamp)

        # Check for duplicates (unless skipped)
        if not skip_duplicate_check:
            similar = self.check_duplicate_records(
                user_id=user_id,
                record_type=record_type,
                timestamp=ts,
                window_minutes=duplicate_window_minutes,
            )
            if similar:
                raise DuplicateRecordError(similar_records=similar)

        # Create record
        record = Record(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            type=record_type,
            timestamp=ts,
            date=ts.date(),
            details=details,
            images=images or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    def check_duplicate_records(
        self,
        user_id: str,
        record_type: str,
        timestamp: datetime,
        window_minutes: int = DEFAULT_DUPLICATE_WINDOW_MINUTES,
    ) -> List[Record]:
        """
        Check for similar records within a time window

        Args:
            user_id: User's UUID
            record_type: Record type to check
            timestamp: Timestamp to check around
            window_minutes: Time window in minutes

        Returns:
            List of similar records found
        """
        window_start = timestamp - timedelta(minutes=window_minutes)
        window_end = timestamp + timedelta(minutes=window_minutes)

        similar = self.db.query(Record).filter(
            and_(
                Record.user_id == uuid.UUID(user_id),
                Record.type == record_type,
                Record.timestamp >= window_start,
                Record.timestamp <= window_end,
            )
        ).all()

        return similar

    def query_records(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        record_type: Optional[str] = None,
    ) -> List[Record]:
        """
        Query records by date range and type

        Args:
            user_id: User's UUID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            record_type: Filter by record type

        Returns:
            List of matching records
        """
        query = self.db.query(Record).filter(Record.user_id == uuid.UUID(user_id))

        # Apply date filters
        if start_date:
            query = query.filter(Record.date >= datetime.strptime(start_date, "%Y-%m-%d").date())
        if end_date:
            query = query.filter(Record.date <= datetime.strptime(end_date, "%Y-%m-%d").date())

        # Apply type filter
        if record_type:
            query = query.filter(Record.type == record_type)

        # Order by timestamp descending
        query = query.order_by(Record.timestamp.desc())

        return query.all()

    def list_daily_records(self, user_id: str, date: Optional[str] = None) -> List[Record]:
        """
        List all records for a specific day

        Args:
            user_id: User's UUID
            date: Date string (YYYY-MM-DD), defaults to today

        Returns:
            List of records for that day
        """
        if date is None:
            target_date = datetime.utcnow().date()
        else:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()

        return self.db.query(Record).filter(
            and_(
                Record.user_id == uuid.UUID(user_id),
                Record.date == target_date,
            )
        ).order_by(Record.timestamp.desc()).all()

    def get_record_by_id(self, user_id: str, record_id: str) -> Optional[Record]:
        """
        Get a single record by ID

        Args:
            user_id: User's UUID (for ownership check)
            record_id: Record's UUID

        Returns:
            Record object if found and owned by user, None otherwise
        """
        return self.db.query(Record).filter(
            and_(
                Record.id == uuid.UUID(record_id),
                Record.user_id == uuid.UUID(user_id),
            )
        ).first()

    def update_record(
        self,
        user_id: str,
        record_id: str,
        details: Optional[dict] = None,
        timestamp: Optional[str] = None,
        images: Optional[List[str]] = None,
    ) -> Record:
        """
        Update an existing record

        Args:
            user_id: User's UUID
            record_id: Record's UUID
            details: Updated details
            timestamp: Updated timestamp
            images: Updated images list

        Returns:
            Updated Record object

        Raises:
            ValueError: If record not found
        """
        record = self.get_record_by_id(user_id, record_id)

        if record is None:
            raise ValueError(f"Record not found: {record_id}")

        # Update fields
        if details is not None:
            record.details = details

        if timestamp is not None:
            new_ts = datetime.fromisoformat(timestamp)
            record.timestamp = new_ts
            record.date = new_ts.date()

        if images is not None:
            record.images = images

        record.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(record)

        return record

    def delete_record(self, user_id: str, record_id: str) -> bool:
        """
        Delete a record

        Args:
            user_id: User's UUID
            record_id: Record's UUID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If record not found
        """
        record = self.get_record_by_id(user_id, record_id)

        if record is None:
            raise ValueError(f"Record not found: {record_id}")

        self.db.delete(record)
        self.db.commit()

        return True


class DuplicateRecordError(Exception):
    """Exception raised when duplicate record is detected"""

    def __init__(self, similar_records: List[Record]):
        self.similar_records = similar_records
        super().__init__(f"Found {len(similar_records)} similar records")