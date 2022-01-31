from asyncio import current_task
from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception as e:
            print(e)
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")
    
    def print_current(self):
        current_tasks = self.current_items
        if len(current_tasks) == 0:
            print('There are no pending tasks!')
        for index, key in enumerate(sorted(self.current_items.keys())):
            print('{}. {} [{}]'.format(index+1, current_tasks[key], key))
            
    def print_completed(self):
        completed_tasks = self.completed_items
        if len(completed_tasks) == 0:
            print('There are no completed tasks!')
        for index, task in enumerate(completed_tasks):
            task = task.strip('\n')
            print("{}. {}".format(index+1, task))

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        priority = int(args[0])
        task = " ".join(args[1:])

        task_in_mem = task
        count = priority

        while(task_in_mem):
            current_task = self.current_items.get(count, None)
            successor_task = self.current_items.get(count + 1, None)

            if current_task:
                self.current_items[count + 1] = current_task
                del self.current_items[count]
            
            self.current_items[count] = task_in_mem
            task_in_mem = successor_task
            count += 1

        self.write_current()
        print('Added task: "{}" with priority {}'.format(task, priority))

    def done(self, args):
        priority = int(args[0])
        completed_task = ""
        if priority in self.current_items:
            completed_task = self.current_items[priority]
            del self.current_items[priority]
            self.write_current()
            self.completed_items.append(completed_task.strip('\n'))
            self.write_completed()
            print("Marked item as done.")
        else:
            print('Error: no incomplete item with priority {} exists.'.format(priority))

    def delete(self, args):
        priority = int(args[0])
        if priority in self.current_items:
            del self.current_items[priority]
            self.write_current()
            print('Deleted item with priority {}'.format(priority))
        else:
            print('Error: item with priority {} does not exist. Nothing deleted.'.format(priority))

    def ls(self):
        self.print_current()

    def report(self):
        print('Pending :', len(self.current_items))
        self.print_current()
        print("\nCompleted :", len(self.completed_items))
        self.print_completed()

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        renderHTML = ''
        current_tasks = self.current_items
        for index, key in enumerate(current_tasks):
            renderHTML += f'''
                <tr>
                    <td>{index+1}</td>
                    <td>{current_tasks[key]}</td>
                    <td>{key}</td>
                </tr>
            '''
        return f"""
            <h1> Show Incomplete Tasks Here </h1>
            <table border="1">
                <tr>
                    <th>#</th>
                    <th>Task</th>
                    <th>Priority</th>
                </tr>
                {renderHTML}
            <table>
        """

    def render_completed_tasks(self):
        # Complete this method to return all completed tasks as HTML
        renderHTML = ''
        completed_tasks = self.completed_items
        print(completed_tasks)
        for index, task in enumerate(completed_tasks):
            renderHTML += f'''
                <tr>
                    <td>{index+1}</td>
                    <td>{task}</td>
                </tr>
            '''
        return f"""
            <h1> Show Completed Tasks Here </h1>
            <table border="1" spaceing="1">
                <tr>
                    <th>#</th>
                    <th>Task</th>
                </tr>
                {renderHTML}
            <table>
        """


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
