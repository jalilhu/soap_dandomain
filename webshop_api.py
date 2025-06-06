# webshop_api.py
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth

class WebshopAPI:
    def __init__(self, wsdl_url, username, password):
        self.wsdl_url = wsdl_url
        self.username = username
        self.password = password
        self.client = None
        self._connect()

    def _connect(self):
        session = Session()
        session.auth = HTTPBasicAuth(self.username, self.password)
        transport = Transport(session=session)
        self.client = Client(self.wsdl_url, transport=transport)

    def add_product(self, product_data: dict):
        """
        Send product data to webshop SOAP API.
        product_data should match the API's expected structure.
        """
        try:
            response = self.client.service.AddProduct(product_data)
            # Adjust method name and parameters according to your actual SOAP API
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to add product: {e}")
