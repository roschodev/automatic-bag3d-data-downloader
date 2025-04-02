from enum import Enum

#ENUM DEFINITION
class Lod(Enum):
    LOW = "1.0"
    MEDIUM = "2.0"
    HIGH = "2.2"

# Define the Enum for the project status
class Status(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
