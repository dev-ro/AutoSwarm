from enum import Enum

class AgentType(str, Enum):
    RESEARCHER = "Researcher"
    SOCIAL = "Social"
    FINANCE = "Finance"
    CODER = "Coder"
    EXECUTIVE = "Executive"
    REVIEWER = "Reviewer"
    TESTER = "Tester"