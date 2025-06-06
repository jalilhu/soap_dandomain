from zeep import Client
from zeep.wsse.username import UsernameToken
import config, os

def send_product(product_data):

    # Path to the WSDL file (ensure service.wsdl is in this directory)
    wsdl_path = os.path.join(os.path.dirname(__file__), 'service.wsdl')
    client = Client(wsdl_path, wsse=UsernameToken(config.USERNAME, config.PASSWORD))
    # Call the Product_Create operation (passing the dict as 'ProductData')
    response = client.service.Product_Create(ProductData=product_data)
    return response  # e.g. the new product ID

def create_product_variant(product_id, variant_data):

    # Path to the WSDL file (ensure service.wsdl is in this directory)
    wsdl_path = os.path.join(os.path.dirname(__file__), 'service.wsdl')
    client = Client(wsdl_path, wsse=UsernameToken(config.USERNAME, config.PASSWORD))
    # Call the Product_Create operation (passing the dict as 'ProductData')
    response = client.service.ProductVariantCreate(ProductData=variant_data)
    return response  # e.g. the new product ID
