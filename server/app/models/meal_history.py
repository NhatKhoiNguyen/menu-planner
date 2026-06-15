from bson import ObjectId
from datetime import datetime
from dateutil.parser import parse as parse_date

class MealHistory:
    def __init__(self, data):
        self.id = str(data.get("_id", ""))
        self.user_id = str(data.get("user_id", ""))
        self.plan = data.get("plan", [])
        raw_date = data.get("date", "")
        if isinstance(raw_date, str):
            try:
                self.date = parse_date(raw_date)
            except Exception:
                self.date = datetime.utcnow()
        elif isinstance(raw_date, datetime):
            self.date = raw_date
        else:
            self.date = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "date": self.date,
            "plan": self.plan
        }
