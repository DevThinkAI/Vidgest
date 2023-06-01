
from datetime import datetime, timezone
from dateutil.parser import parse
import re

class DateHelper:

    @staticmethod
    def get_days_ago(date_string) -> int:
        """
        Get the number of days ago from a date string.
        """
        date = parse(date_string)
        now = datetime.now(timezone.utc)
        return (now - date).days
    
    @staticmethod
    def duration_to_human_readable(duration):
        """
        Convert an ISO 8601 duration string to a human readable string.
        """
        if duration is None:
            return None
        # Regular expression to match ISO 8601 durations
        pattern = re.compile(r'P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)(?:D|W))?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?')
        
        # Try to match the pattern
        match = pattern.match(duration)
        if match:
            parts = match.groups()
            
            # Get the parts of the duration
            years = parts[0] and f"{int(parts[0])} years" or ""
            months = parts[1] and f"{int(parts[1])} months" or ""
            days_or_weeks = parts[2] and f"{int(parts[2])} days" or ""
            hours = parts[3] and f"{int(parts[3])} hours" or ""
            minutes = parts[4] and f"{int(parts[4])} minutes" or ""
            seconds = parts[5] and f"{float(parts[5])} seconds" or ""
            
            # Construct the human-readable string
            human_readable = " ".join(filter(bool, [years, months, days_or_weeks, hours, minutes, seconds]))
            
            return human_readable
        else:
            return "Invalid duration"

