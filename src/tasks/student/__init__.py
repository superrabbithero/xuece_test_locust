"""学生任务模块"""
from .user_homepage import UserHomepageBehavior
from .holiday_task import HolidayTaskListBehavior
from .watch_video import WatchVideoBehavior
from .outdoor_training import DoOutdoorTraining
from .ask_question import StuAskQuestion
from .download import DownloadBehavior
from .homework_free import DoHomeworkFree
from .schedule_task import DoScheduleTask
from .registration_service import RegistrationServiceBehavior
from .login_only import LoginOnlyBehavior

__all__ = [
    'UserHomepageBehavior',
    'HolidayTaskListBehavior',
    'WatchVideoBehavior',
    'DoOutdoorTraining',
    'StuAskQuestion',
    'DownloadBehavior',
    'DoHomeworkFree',
    'DoScheduleTask',
    'RegistrationServiceBehavior',
    'LoginOnlyBehavior',
]

