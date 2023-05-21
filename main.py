import threading
import datetime

import selenium
import selenium.webdriver
from selenium.webdriver.common.by import By

from links import google_sheet, links, systems


class CustomThread(threading.Thread):
	thread_data = {}

	def __init__(self, link, system, name):
		"""
		:param link: link to the logs
		:param system: system name
		:param name: student name
		"""
		super().__init__()
		self.link = link
		self.system = system
		self.name = name

	def run(self):
		"""
		:return: result of the thread
		"""
		result = self.get_results(self.link, self.system, self.name)
		self.set_data(result)

	@staticmethod
	def get_results(link, system, name):
		"""
		:param link: link to the logs
		:param system: system name
		:param name: student name
		:return: auto-tests results on the exact system
		"""
		options = selenium.webdriver.ChromeOptions()
		options.add_argument('headless')
		webdriver = selenium.webdriver.Chrome(options=options)
		webdriver.get(link)
		students = webdriver.find_elements(By.TAG_NAME, "tr")
		columns = students[0].text.split()
		result = f"--{system}--\n"
		for student in students:
			info = student.text.split()
			info = [" ".join([info[0], info[1], info[2]])] + info[3:]
			if name in info:
				for i in range(len(columns)):
					result += f"{columns[i]}: {info[i]}\n"
		return result

	@staticmethod
	def get_current_mark(name: str, link_to_table: str) -> str:
		"""
		:param name: student name
		:param link_to_table: link to Google sheet
		:return: student current mark
		"""
		options = selenium.webdriver.ChromeOptions()
		options.add_argument('headless')
		webdriver = selenium.webdriver.Chrome(options=options)
		webdriver.get(link_to_table)
		students = webdriver.find_elements(By.TAG_NAME, "tr")[1:]
		result = ""
		for student in students:
			if len(student.text) == 0:
				continue
			info = student.text.split()
			info = [" ".join([info[0], info[1], info[2]])] + info[3:]
			if name in info:
				result += info[2]
		return result

	def set_data(self, data):
		self.thread_data[self.ident] = data

	@classmethod
	def get_data(cls):
		return [cls.thread_data[thread_id] for thread_id in cls.thread_data]


def main():
	name = ""  # Your ФИО goes here

	threads_number = 3
	threads = []
	for number in range(threads_number):
		t = CustomThread(links[number], systems[number], name)
		t.start()
		threads.append(t)

	for thread in threads:
		thread.join()

	data = CustomThread.get_data()

	failed_tests = 0
	for i in range(len(data)):
		failed_tests += data[i].count(" −")

	with open("output.txt", "w") as file:
		for thread_data in data:
			file.write(thread_data)
			file.write(("~" * 30) + "\n")
		file.write(f"\nCurrent mark: {CustomThread.get_current_mark(name, google_sheet)}\n\n")
		file.write(("=" * 30) + "\n")
		file.write("AutoTests\n")
		file.write(f"{failed_tests} tests failed\n")
		file.write(f"Version: {datetime.datetime.now()}\n")


if __name__ == '__main__':
	main()
