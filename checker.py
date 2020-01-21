# Декоратор должен проверять вошёлли пользователь в систему 

from flask import session

from functools import wraps

def check_logged_in(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'logged_in' in session:
			return func(*args, **kwargs)
		else:
			return "ERROR YOU DONT LOGGIN"
	return wrapper

