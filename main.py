import datetime
import sys
import requests

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLineEdit, QLabel, QMessageBox, QCheckBox

base_url = "https://workflow-manager-server.herokuapp.com/workflow-manager-api"

class MainForm(QWidget):

    def __init__(self):
        super().__init__()
        self.token = None
        self.setWindowTitle('Login Form')
        self.resize(500, 120)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        layout = self.layout

        label_name = QLabel('<font size="4"> Username </font>')
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('Please enter your username')
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel('<font size="4"> Password </font>')
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText('Please enter your password')
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton('Login')
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 2, 0, 1, 2)

    def check_password(self):
        url = base_url + "/authentication/createAuthenticationToken"
        body = {
            'username': self.lineEdit_username.text(),
            'plainPassword': self.lineEdit_password.text(),
        }
        x = requests.get(url, params=body)
        msg = QMessageBox()

        print(x.status_code)
        print(x.json())
        if x.status_code == 200:
            msg.setWindowTitle("Success")
            msg.setText('Successfully logged in')
            msg.exec_()
            self.token = x.json()["token"]
            self.show_worker_panel()
        else:
            msg.setWindowTitle("Failure")
            msg.setText('Incorrect password or username')
            msg.exec_()

    def show_worker_panel(self):
        print(self.token)
        self.setWindowTitle('Worker Panel')
        self.resize(500, 250)
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        layout = self.layout
        task_title = QLabel('<font size="6"> Task Details </font>')
        task_name_label = QLabel('<font size="4"> Task name: </font>')
        task_description_label = QLabel('<font size="4"> Task description: </font>')
        task_deadline_label = QLabel('<font size="4"> Task deadline: </font>')
        task_localization_label = QLabel('<font size="4"> Task localization: </font>')
        task_report_label = QLabel('<font size="6"> Task Report form </font>')
        self.task_description_data = QLabel('')
        self.task_name_data = QLabel('')
        self.task_deadline_data = QLabel('')
        self.task_localization_data = QLabel('')
        task_report_description_label = QLabel('<font size="4"> Result description: </font>')
        task_report_success_label = QLabel('<font size="4"> Was successful?: </font>')
        self.task_report_description_data = QLineEdit()
        self.task_report_description_data.setPlaceholderText('Please enter task description')
        self.task_report_success_data = QCheckBox()
        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.send_task_report)
        layout.addWidget(task_title, 0, 0)
        layout.addWidget(task_name_label, 1, 0)
        layout.addWidget(self.task_name_data, 1, 1)
        layout.addWidget(task_description_label, 2, 0)
        layout.addWidget(self.task_description_data, 2, 1)
        layout.addWidget(task_deadline_label, 3, 0)
        layout.addWidget(self.task_deadline_data, 3, 1)
        layout.addWidget(task_localization_label, 4, 0)
        layout.addWidget(self.task_localization_data, 4, 1)
        layout.addWidget(task_report_label, 5, 0)
        layout.addWidget(task_report_description_label, 6, 0)
        layout.addWidget(self.task_report_description_data, 6, 1)
        layout.addWidget(task_report_success_label, 7, 0)
        layout.addWidget(self.task_report_success_data, 7, 1)
        layout.addWidget(submit_button, 8, 0, 1, 7)
        self.check_next_task()

    def check_next_task(self):
        url = base_url + "/task/current"
        body = {}
        headers = {'AUTHORIZATION': self.token}
        task = requests.get(url, params=body, headers=headers)
        print(task.json())
        if task.status_code != 200:
            url = base_url + "/task/next"
            body = {"autoStart": "true"}
            headers = {'AUTHORIZATION': self.token}
            task = requests.get(url, params=body, headers=headers)
            print(task.json())
        if task.status_code == 200:
            self.task_json = task.json()
            self.task_description_data.setText(self.task_json["description"])
            self.task_name_data.setText(self.task_json["name"])
            self.task_deadline_data.setText(self.task_json["deadline"])
            localization_id = int(self.task_json["localizationId"])
            url = base_url + "/localization"
            body = {}
            headers = {'AUTHORIZATION': self.token}
            localizations = requests.get(url, params=body, headers=headers).json()
            for localization in localizations:
                if int(localization["id"]) == localization_id:
                    self.task_localization_data.setText(localization["name"])
        else:
            msg = QMessageBox()
            msg.setWindowTitle("End of work")
            msg.setText('No pending tasks - click to finish')
            msg.exec_()
            main_form.close()

    def send_task_report(self):
        task_description = self.task_report_description_data.text()
        if self.task_report_success_data.checkState() == 2:
            task_result = "true"
        else:
            task_result = "false"
        url = base_url + "/taskWorkerReport"
        body = {
            'description': task_description,
            'success': task_result,
            'taskId': int(self.task_json['id'])
        }
        headers = {'AUTHORIZATION': self.token}
        result = requests.post(url, json=body, headers=headers)
        print(result.json())
        if 200 <= result.status_code < 300:
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText('Successfully finished task')
            msg.exec_()
            self.check_next_task()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Failure")
            msg.setText('Failed to submit task result - check input')
            msg.exec_()


app = QApplication(sys.argv)
main_form = MainForm()
main_form.show()
sys.exit(app.exec_())

