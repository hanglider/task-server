class TaskManager:
    def __init__(self):
        self.queue = {"tasks": [], "datas": []}
        self.slave_hosts = ['192.168.1.107:5001']
        self.available_hosts = self.slave_hosts.copy()
        self.main_file_index = 0

    def add_file_to_queue(self, filename: str):
        if "task" in filename:
            self.queue["tasks"].append(filename)
        elif "image" in filename:
            self.queue["datas"].append(filename)


task_manager = TaskManager()
