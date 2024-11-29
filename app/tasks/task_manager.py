class TaskManager:
    def __init__(self):
        self.queue = []
        self.results = {}
        self.slave_hosts = ['192.168.1.107:5001']
        self.available_hosts = self.slave_hosts.copy()
        self.main_file_index = 0

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

    def add_file_to_queue(self, part_name: str, task_name: str):
        dictionary = (part_name, task_name)
        self.queue.append(dictionary)


task_manager = TaskManager()
