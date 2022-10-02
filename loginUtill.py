import re
import sqlite3
import pymysql
import pymongo
import requests
from flask import session, g, render_template, redirect, url_for

class Protection:
	def __init__(self):
		try:
			connect = sqlite3.connect(f'Protection.db')
			cursor = connect.cursor()
			cursor.execute(f'create table blacklist(ip)')
			cursor.execute(f'create table whitelist(ip)')
			cursor.execute(f'create table proxies(ip)')
			cursor.close()
			connect.close()
		except:
			pass

	def blacklist(self):
		connect = sqlite3.connect('Protection.db')
		cursor = connect.cursor()
		cursor.execute(f"SELECT * FROM blacklist")
		r = cursor.fetchall()
		connect.close()
		return r
	
	def add_blacklist(self, ip):
		try:
			connect = sqlite3.connect('Protection.db')
			cursor = connect.cursor()
			cursor.execute(f"insert into blacklist values (f'{ip}'")
			connect.commit()
			cursor.close()
			connect.close()
			return [True, 'success']
		except Exception as e:
			cursor.close()
			connect.close()
			return [False, e]
	
	def remove_blacklist(self, ip):
		try:
			connect = sqlite3.connect('Protection.db')
			cursor = connect.cursor()
			cursor.execute(f"DELETE FROM accounts WHERE ip = {ip}")
			connect.commit()
			cursor.close()
			connect.close()
			return [True, 'success']
		except Exception as e:
			cursor.close()
			connect.close()
			return [False, e]
	
	def check_proxies(self, ip):
		try:
			res = requests.get(f'https://proxycheck.io/v2/{ip}?key=8n3369-6l9285-663588-8556oa&vpn=1').json()
			if res['status'] == 'ok':
				r = res['type']
				if res['proxy'] == 'yes':
					return [True, str(r)]
				else:
					return [False, str(r)]
			else:
				return [True, 'unknown ip adress']
		except Exception as e:
			return [None, str(e)]

class Assets:
	def __init__(self,
	data_index: list = ['email', 'username', 'password'],
	database_type: str = 'SQLite',
	database_name: str = 'AccountsData',
	database_connection_information: dict = None,
	primary_identifier: str = 'email'
	):
		"""
		Only SQLite can be used in the database type. (MySQL and MongoDB will be updated soon.)
		database_connection_information is a variable that is not currently used.

		config['REQUIRE_EMAIL_VERIFY'] is also not available in this version.

		'code example'

		from flask import Flask
		from flask import session, g, render_template, url_for, flash, redirect
		from loginUtill import *

		app = Flask(__name__)
		app.secret_key = 'secret_key'

		UserManager = Flask_Login_Utills() #also you can use Flask_Login_Utills(['email', 'username', 'discord', 'password'], 'SQLite', 'Acc', 'email', '/')
		UserManager.config['SESSION_NAME'] = 'userdata'
		UserManager.config['USER_ACCESS_LEVELS'] = ['ADMIN', 'USER'] #user's access level list
		UserManager.config['DUPLICATE_EMAIL'] = False #True = deny duplicate email
		UserManager.config['ANTI_DUPLICATE_INDEX'] = ['username', 'discord'] #deny duplicate in data index
		"""
		self.data_index = data_index
		self.data_index.append('level')
		self.database_name = database_name
		self.database_connection_information = database_connection_information
		self.primary_identifier = primary_identifier
		if database_type != "SQLite":
			self.database_type = "SQlite"
		else:
			self.database_type = database_type
		self.user_access_levels = ['ADMIN', 'USER']
		self.config = {'SESSION_NAME': 'userdata', 'REQUIRE_EMAIL_VERIFY': False, 'USER_ACCESS_LEVELS': ['ADMIN', 'USER'], 'DUPLICATE_EMAIL': True, "REQUIRE_SPECIAL_CHAR_IN_PASSWORD": False, "REQUIRE_UPPERCASE_CHAR_IN_PASSWORD": False, 'ANTI_DUPLICATE_INDEX': None, 'REDIRECT_PAGE': '/', 'LOGOUT_REDIRECT': '/login'}
	
	def create_database_task(self):
		"""
		Don't use this function.
		This is a login database generation function, which runs automatically.
		"""
		if self.database_type == "SQLite":
			try:
				n = 0
				for i in self.data_index:
					n += 1
					if n == 1:
						indexes = f"{i}"
					else:
						indexes = f"{indexes}, {i}"
				connect = sqlite3.connect(f'{self.database_name}.db')
				cursor = connect.cursor()
				cursor.execute(f'create table accounts({indexes})')
				cursor.close()
				connect.close()
			except:
				pass

	def create_accounts(self, parameters: dict):
		"""
		Account Register Function.

		'code example'
		
		UserManager = Flask_Login_Utills()
		res = UserManager.create_accounts({'email': 'testaccount@gmail.com', 'username': 'mintsoda', 'password': 'password'})
		if res[0] == Flase:
			#register failed (reason: res[1])
		else:
			#Execute Success Phase (ex: redirect) [Automatic login does not work. (Need to move the login page separately)]
		"""
		try:
			n = 0
			for index, i in parameters.items():
				n += 1
				if n == 1:
					values = f"'{i}'"
				else:
					values = f"{values}, '{i}'"
			self.create_database_task()
			self.processing = True
			if self.config['DUPLICATE_EMAIL'] == False:
				connect = sqlite3.connect(f'{self.database_name}.db')
				cursor = connect.cursor()
				cursor.execute(f"SELECT EXISTS(SELECT * FROM accounts WHERE email='{parameters['email']}')")
				if cursor.fetchone() == (1,):
					self.processing = False
					return [False, "Early exists email."]
				else:
					pass
				cursor.close()
				connect.close()
			if self.config['ANTI_DUPLICATE_INDEX'] != None:
				for i in self.config['ANTI_DUPLICATE_INDEX']:
					connect = sqlite3.connect(f'{self.database_name}.db')
					cursor = connect.cursor()
					cursor.execute(f"SELECT EXISTS(SELECT * FROM accounts WHERE {i}='{parameters[i]}')")
					if cursor.fetchone() == (1,):
						self.processing = False
						return [False, f"Early exists values ({i})"]
					else:
						pass
			if self.processing == True:
				level = self.config['USER_ACCESS_LEVELS'][len(self.config['USER_ACCESS_LEVELS'])-1]
				connect = sqlite3.connect(f'{self.database_name}.db')
				cursor = connect.cursor()
				cursor.execute(f"insert into accounts values ({values}, '{level}')")
				connect.commit()
				cursor.close()
				connect.close()
				del self.processing
				return [True, "success"]
		except:
			return [False, "Database Error (Pleace check indexes.)"]
	
	def delete_accounts(self, parameters: dict):
		"""
		Account Delete Function

		'code example'

		UserManager = Flask_Login_Utills()
		res = UserManager.delete_accounts({'email': 'testaccount@gmail.com', 'username': 'mintsoda', 'password': 'password'})
		if res[0] == Flase:
			#delete failed (reason: res[1])
		else:
			#Execute Success Phase (ex: redirect)
		"""
		try:
			n = 0
			for index, value in parameters.items():
				n += 1
				if n == 1:
					wheres = f"{index} = '{value}'"
				else:
					wheres = f"{wheres} and {index} = '{value}'"
			connect = sqlite3.connect(f'{self.database_name}.db')
			cursor = connect.cursor()
			cursor.execute(f"SELECT EXISTS(SELECT * FROM accounts WHERE {wheres})")
			if cursor.fetchone() == (1,):
				cursor.execute(f"DELETE FROM accounts WHERE {wheres}")
				connect.commit()
				cursor.close()
				connect.close()
				return [True, "success"]
			else:
				cursor.close()
				connect.close()
				return [False, "Account doesn't exist."]
		except:
			return [False, "Can't delete userdata (Please check values.)"]
	
	def login(self, parameters: dict):
		"""
		Login Function

		WARNING: Login discrimination must not contain duplicateable indexes. (However, the password is an exception.)

		'code example'

		UserManager = Flask_Login_Utills()
		res = UserManager.login({'username': 'mintsoda', 'password': 'password'})
		if res[0] == Flase:
			#register failed (reason: res[1])
		else:
			#Execute Success Phase (ex: redirect) [Automatic login work. Don't redirect login page.]
			#Also support redirect at UserManager.config['REDIRECT_PAGE']. Useage: return res[1] [Default: '/']
		"""
		try:
			n = 0
			for index, value in parameters.items():
				n += 1
				if n == 1:
					wheres = f"{index} = '{value}'"
				else:
					wheres = f"{wheres} and {index} = '{value}'"
			connect = sqlite3.connect(f'{self.database_name}.db')
			cursor = connect.cursor()
			cursor.execute(f"SELECT EXISTS(SELECT * FROM accounts WHERE {wheres})")
			if cursor.fetchone() == (1,):
				cursor.close()
				connect.close()
				try:
					session[self.config['SESSION_NAME']] = parameters[self.primary_identifier]
				except:
					try:
						session[self.config['SESSION_NAME']] = parameters['email']
					except:
						try:
							session[self.config['SESSION_NAME']] = parameters['username']
						except:
							try:
								session[self.config['SESSION_NAME']] = parameters['uuid']
							except:
								return [False, 'Failed to detect season identifier.']
				return [True, redirect(self.redirect_page)]
			else:
				return [False, 'id or password missmatch.']
		except:
			return [False, 'Unknown Error']
	
	def logout(self):
		"""
		Logout Function

		'code example'

		UserManager = Flask_Login_Utills()
		res = UserManager.logout()
		if res[0] == Flase:
			#register failed (reason: res[1])
		else:
			#Execute Success Phase (ex: redirect)
			#Also support redirect at UserManager.config['LOGOUT_REDIRECT']. Useage: return res[1] [Default: '/login']
		"""
		if session.get(self.config['SESSION_NAME']):
			del session[self.config['SESSION_NAME']]
			return [True, self.config['LOGOUT_REDIRECT']]
		else:
			return [False, 'Early logouted.']
		
	
	def isproxy(self, request):
		try:
			check = Protection()
			c = check.check_proxies(request.remote_addr)
			if c == True:
				return [True, 'connect ip adress is proxy.']
			elif c == False:
				return [False, 'connect ip adress is not proxy.']
			else:
				return [None, 'occur error.']
		except:
			return [None, 'unknown error']

class Flask_Login_Utills(Assets):
	pass

# a = Flask_Login_Utills()
# a.config['DUPLICATE_EMAIL'] = True
# a.config['ANTI_DUPLICATE_INDEX'] = ['username', 'password']
# print(a.login({'email': "test@gmail.com", 'username': "mintsoda", 'password': "testacc123"}))