# Import pymysql and install it as the default MySQLdb driver
# This tricks Django into using PyMySQL without changing the ENGINE in settings.py
import pymysql

pymysql.version_info = (2, 2, 4, "final", 0) # Engañamos a Django con la versión
pymysql.install_as_MySQLdb()