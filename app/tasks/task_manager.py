from asyncio import Lock

class TaskManager:
    def __init__(self):
        self.queue = []
        self.available_hosts = []
        self.results = {}
        self.main_file_index = 0
        self.lock = Lock()

    def add_file_to_queue(self, data_file, task_file):
        self.queue.append((data_file, task_file))

    def add_host(self, host):
        self.available_hosts.append(host)

    def add_result_to_list(self, meta_data: str, result):
        num_part, index, num_splits = map(int, meta_data.replace('!', ' ').replace('$', ' ').split())
        if index not in self.results:
            self.results[index] = []
        self.results[index].append((num_part, result))
        if index not in self.results:
            return False, -1
        if len(self.results[index]) == num_splits:
            return True, index
        else:
            return False, -1


task_manager = TaskManager()
