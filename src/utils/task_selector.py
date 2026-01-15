"""任务选择器模块"""
from typing import List, Optional
from config import get_settings
from src.tasks.student import (
    UserHomepageBehavior,
    HolidayTaskListBehavior,
    WatchVideoBehavior,
    DoOutdoorTraining,
    StuAskQuestion,
    DownloadBehavior,
    DoHomeworkFree,
    DoScheduleTask,
    RegistrationServiceBehavior,
    LoginOnlyBehavior,
)
from src.tasks.teacher import TchMarkingList
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 任务映射表
TASK_MAP = {
    # 学生任务
    'user_homepage': UserHomepageBehavior,
    'holiday_task': HolidayTaskListBehavior,
    'watch_video': WatchVideoBehavior,
    'outdoor_training': DoOutdoorTraining,
    'ask_question': StuAskQuestion,
    'download': DownloadBehavior,
    'homework_free': DoHomeworkFree,
    'schedule_task': DoScheduleTask,
    'registration_service': RegistrationServiceBehavior,
    'login_only': LoginOnlyBehavior,
    # 教师任务
    'marking_list': TchMarkingList,
}

# 任务组
TASK_GROUPS = {
    'all': list(TASK_MAP.keys()),
    'student': [
        'user_homepage',
        'holiday_task',
        'watch_video',
        'outdoor_training',
        'ask_question',
        'download',
        'homework_free',
        'schedule_task',
        'registration_service',
        'login_only',
    ],
    'teacher': [
        'marking_list',
    ],
}


def select_tasks(
    account_type: str = 'stu',
    task_config: Optional[str] = None
) -> List:
    """
    根据配置选择要执行的任务
    
    Args:
        account_type: 账号类型 ('stu' 或 'tch')
        task_config: 任务配置字符串，格式：
            - "all" - 所有任务
            - "student" - 所有学生任务
            - "teacher" - 所有教师任务
            - "task1,task2" - 指定任务列表，用逗号分隔
            - None - 使用配置中的 SELECTED_TASKS
    
    Returns:
        List: 选中的任务类列表
    """
    settings = get_settings()
    
    # 如果没有提供task_config，使用配置中的值
    if task_config is None:
        task_config = getattr(settings, 'SELECTED_TASKS', None)
    
    # 如果没有配置，使用默认行为（根据账号类型）
    if not task_config:
        if account_type == 'stu':
            return [
                UserHomepageBehavior,
                HolidayTaskListBehavior,
                WatchVideoBehavior,
                DoOutdoorTraining,
                StuAskQuestion,
                DownloadBehavior,
                DoScheduleTask,
                RegistrationServiceBehavior
            ]
        else:
            return [TchMarkingList]
    
    # 解析任务配置
    task_config = task_config.strip().lower()
    selected_task_names = []
    
    # 处理任务组
    if task_config in TASK_GROUPS:
        selected_task_names = TASK_GROUPS[task_config]
    else:
        # 处理逗号分隔的任务列表
        task_list = [name.strip() for name in task_config.split(',')]
        
        # 检查是否有指定账号类型的任务（格式: student:task_name 或 teacher:task_name）
        for task_item in task_list:
            if ':' in task_item:
                # 格式: student:task_name 或 teacher:task_name
                parts = task_item.split(':', 1)
                if len(parts) == 2:
                    specified_type = parts[0].strip()
                    task_name = parts[1].strip()
                    
                    # 检查指定的账号类型是否匹配当前账号类型
                    if specified_type == 'student' and account_type == 'stu':
                        selected_task_names.append(task_name)
                    elif specified_type == 'teacher' and account_type == 'tch':
                        selected_task_names.append(task_name)
                    # 如果不匹配，忽略该任务
                else:
                    selected_task_names.append(task_item)
            else:
                # 普通任务名称
                selected_task_names.append(task_item)
    
    # 根据账号类型过滤任务（确保任务在对应账号类型的任务列表中）
    if account_type == 'stu':
        # 学生账号只能执行学生任务
        student_tasks = TASK_GROUPS['student']
        selected_task_names = [name for name in selected_task_names if name in student_tasks]
    else:
        # 教师账号只能执行教师任务
        teacher_tasks = TASK_GROUPS['teacher']
        selected_task_names = [name for name in selected_task_names if name in teacher_tasks]
    
    # 转换为任务类
    selected_tasks = []
    invalid_tasks = []
    
    for task_name in selected_task_names:
        if task_name in TASK_MAP:
            selected_tasks.append(TASK_MAP[task_name])
        else:
            invalid_tasks.append(task_name)
    
    # 记录日志
    if invalid_tasks:
        logger.warning(f"无效的任务名称: {invalid_tasks}")
        logger.info(f"可用任务: {', '.join(TASK_MAP.keys())}")
    
    if not selected_tasks:
        logger.warning(f"没有选中任何任务，使用默认任务")
        # 返回默认任务
        if account_type == 'stu':
            return [
                UserHomepageBehavior,
                HolidayTaskListBehavior,
                WatchVideoBehavior,
                DoOutdoorTraining,
                StuAskQuestion,
                DownloadBehavior,
                DoScheduleTask,
                RegistrationServiceBehavior
            ]
        else:
            return [TchMarkingList]
    
    logger.info(
        f"账号类型: {account_type}, "
        f"选中任务: {', '.join(selected_task_names)} "
        f"({len(selected_tasks)}个任务)"
    )
    
    # 如果配置了任务但被过滤掉了，给出提示
    if task_config and task_config not in TASK_GROUPS:
        original_tasks = [name.strip() for name in task_config.split(',')]
        filtered_out = [name for name in original_tasks if name not in selected_task_names]
        if filtered_out:
            logger.info(
                f"以下任务被过滤（不在{account_type}账号类型的任务列表中）: {', '.join(filtered_out)}"
            )
    
    return selected_tasks


def get_available_tasks() -> dict:
    """
    获取所有可用的任务列表
    
    Returns:
        dict: 包含任务组和任务映射的字典
    """
    return {
        'task_map': TASK_MAP,
        'task_groups': TASK_GROUPS
    }

