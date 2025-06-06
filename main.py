from soap.soap_client import DandomainSOAPClient
from pprint import pprint
from zeep.helpers import serialize_object
from ui.main_ui import launch_main_ui
from ui.product_variant_ui import launch_custom_data_ui
import os
import sys
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
db_path = os.path.join(BASE_DIR, 'products.db')
wsdl_relative = os.getenv("DANDOMAIN_WSDL")  # 'service.wsdl'
wsdl_path = os.path.join(BASE_DIR, wsdl_relative)
# Connect to the database
conn = sqlite3.connect(db_path)
    
    
# Get All the Products from the Dandomain API
##############################################################################################################
# client = DandomainSOAPClient()
# custom_data = client.get_al_site()
# print(custom_data)
# ##############################################################################################################



# Get all the Categories from the dandomain API
##############################################################################################################
# client = DandomainSOAPClient()
# categories = client.get_category_all()
# for category in categories:
#     print(category)
##############################################################################################################

# Launch the main UI to create a new product
##############################################################################################################
product_id = launch_main_ui()

if product_id:  # If a product was created successfully
    launch_custom_data_ui(product_id)

##############################################################################################################



