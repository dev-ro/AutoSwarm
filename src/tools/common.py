from datetime import datetime
import pytz 
from agno.tools import Toolkit

class CommonTools(Toolkit):
    def __init__(self):
        super().__init__(name="common_tools")
        self.register(self.get_current_time)

    def get_current_time(self, timezone: str = "US/Eastern") -> str:
        """
        Returns the current time in the specified timezone.
        """
        try:
            tz = pytz.timezone(timezone)
            return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception as e:
            return f"Error: {e}"
