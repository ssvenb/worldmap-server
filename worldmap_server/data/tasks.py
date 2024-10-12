class DataProvider:
    def __init__(self, taskManager, _):
        self.taskManager = taskManager

    def get_all(self):
        return self.taskManager.ui_types
