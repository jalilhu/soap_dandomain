from zeep import Client
import pprint


from config import DANDOMAIN_WSDL, DANDOMAIN_USER, DANDOMAIN_PASS

class DandomainSOAPClient:
    def __init__(self):
        self.client = Client(DANDOMAIN_WSDL)
        self.client.service.Solution_Connect(Username=DANDOMAIN_USER, Password=DANDOMAIN_PASS)
        # self.set_fields('Id,Title,Status,ProducerId,UnitId,ItemNumber,ItemNumberSupplier,Ean,Sorting,DateCreated,DateUpdated,Description,DescriptionLong,DescriptionShort,CategoryId,SecondaryCategoryIds,BuyingPrice,Price,Pictures,SeoTitle,SeoDescription,SeoKeywords,SeoLink,SeoCanonical,Variants,VariantTypes,CustomData')
        # self.set_fields('Title,Status,ProducerId,UnitId,ItemNumber,ItemNumberSupplier,Ean,Sorting,Description,DescriptionLong,DescriptionShort,CategoryId,SecondaryCategoryIds,BuyingPrice,Price,Pictures,SeoTitle,SeoDescription,SeoKeywords')
        self.set_fields('Id,ProducerId,Title,UnitId,Type')
        # self.client.service.Product_SetVariantFields(Fields='Id,Sorting,Title')
    
    def set_fields(self, fields_str):
        self.client.service.Product_SetFields(Fields=fields_str)

    def remove_custom_data(self, custom_data_id):
            response =self.client.service.Product_DeleteCustomData(ProductCustomDataId=custom_data_id)
            print(f"Deleted custom data with ID {custom_data_id}: {response}")
            
    def product_remove_custom_data(self, product_id, custom_data_id):
        try:
            response = self.client.service.Product_RemoveCustomData(
                ProductId=product_id,
                CustomDataId=custom_data_id
            )
            print(f"Removed custom data {response}")
            return response
        except Exception as e:
            print(f"Error removing custom data: {e}")
            raise

        # Add the updated custom data
        # for custom_data in custom_data_updates:
        #     response = self.client.service.Product_AddCustomData(
        #         ProductId=product_id,
        #         CustomDataId=custom_data['CustomDataId'],
        #     )
        #     print(f"Added custom data with ID {custom_data['CustomDataId']}: {response}")
            
    def add_new_custom_data(self, custom_data_updates):
        
        response = self.client.service.Product_CreateCustomData(ProductCustomData=custom_data_updates)
        print(f"Added custom data with ID {custom_data_updates['ProductCustomId']}: {response}")
        
    def create_new_category(self, category_data):
        try:
            response = self.client.service.Category_Create(CategoryData=category_data)
            print(f"Created new category with ID {response}")
            return response
        except Exception as e:
            print(f"Error creating category: {e}")
            raise
        
    def get_category_all(self):
        try:
            response = self.client.service.Category_GetAll()
            print(f"Fetched all categories: {response}")
            return response
        except Exception as e:
            print(f"Error fetching categories: {e}")
            raise
        
    def add_custom_data_to_product(self, product_id, custom_data_id):
        try:
            response = self.client.service.Product_AddCustomData(
                ProductId=product_id,
                CustomDataId=custom_data_id
            )
            print(f"Added custom data {response}")
            return response
        except Exception as e:
            print(f"Error adding custom data: {e}")
            raise

    def get_fields_update_product_custom_data(self):
        update_custom_data = self.client.get_type('ns0:ProductCustomDataUpdate')
        print(update_custom_data)
        return update_custom_data        
    
    def get_fields_update_product_custom_data_type(self):
        update_custom_data_type = self.client.get_type('ns0:ProductCustomDataTypeUpdate')
        print(update_custom_data_type)
        return update_custom_data_type
        
    def get_product_custom_data_type(self, product_id):
        response2 = self.client.service.Product_GetCustomDataType(CustomDataTypeId=product_id)
        print(f"Custom data for product {product_id}: {response2}")
        return response2
        
        
    def get_product_custom_data(self, product_id):
        response = self.client.service.Product_GetCustomData(ProductId=product_id)
        # response2 = self.client.service.Product_GetCustomDataAll()
        print(f"Custom data for product: {response}")
        return response
    def get_all_custom_data(self):
        # Fetch all custom data types
        response = self.client.service.Product_GetCustomDataTypeAll()
        print(f"All custom data types: {response}")
        return response
    def get_al_site(self):
        # Fetch all custom data types
        response = self.client.service.Sites_GetAll()
        return response

    def update_custom_data(self, data):
        # Ensure all required fields are present
        # required_fields = ["Id", "Sorting", "Title"]
        # for field in required_fields:
        #     if field not in data:
        #         raise ValueError(f"Missing required field: {field}")

    # Call the SOAP operation with unpacked arguments
        response = self.client.service.Product_UpdateCustomData(ProductCustomData=data)
        print(f"Update response: {response}")
        return response
   
    
    def create_product(self, product_obj):
        # product_obj must be a dict or object matching WSDL fields
        response = self.client.service.Product_Create(ProductData=product_obj)
        return response
    def get_all_products(self):
        
        product_return = self.client.service.Product_GetAll()
        products = product_return
        return products
    
    def get_product_by_id(self, product_id):
        product_data = self.client.service.Product_GetById(ProductId=product_id)
        existing_custom_data = product_data.CustomData.item  # this is a list
        print(f"Custom data for product {product_id}: {existing_custom_data}")

        
        return existing_custom_data
    

        return True
    
    def create_product_variant(self, variant_data):
        # file_type = self.client.get_type('ns0:ProductVariantCreate')
        
        
        # return file_type
        # """
        # Creates a new product variant using the Product_CreateVariant operation.
        
        # :param variant_data: Dictionary containing variant data matching ProductVariantCreate fields.
        # :return: Response from server (typically variant ID or result code)
        # """
        try:
            response = self.client.service.Product_CreateVariant(**variant_data )
            print(response)
            return response
        except Exception as e:
            print(f"Error creating variant: {e}")
            raise


    def fetch_and_print_products(self):
    # Set which fields to retrieve for products and variants
        self.client.service.Product_SetFields('Id,CategoryId,Category,SecondaryCategoryIds,SecondaryCategories,ProducerId,Producer,Online,Status,DisableOnEmpty,CallForPrice,Stock,ItemNumber,ItemNumberSupplier,RelationCode,Url,Weight,BuyingPrice,Price,Discount,DiscountType,Delivery,DeliveryId,DeliveryTime,DeliveryTimeId,DiscountGroupId,DiscountGroup,Ean,FocusFrontpage,FocusCart,DateCreated,DateUpdated,RelatedProductIds,LanguageISO,Title,SeoTitle,SeoDescription,SeoKeywords,SeoLink,SeoCanonical,Description,DescriptionShort,DescriptionLong,Variants,Tags,Pictures,CustomData,Additionals,ExtraBuyRelations,UnitId,Unit,UserAccess,UserAccessIds,UserGroupAccess,UserGroupAccessIds,Discounts,MinAmount,VariantTypes,Sorting,GuidelinePrice,ProductUrl,Type,PacketProducts,LanguageAccess,VatGroupId,VatGroup,AutoStock,CategorySortings,OutOfStockBuy,StockLow,StockLocations')
        # self.client.service.Product_SetVariantFields("Id,Stock,StockLow,Price,BuyingPrice,ItemNumber,ItemNumberSupplier,Weight,DeliveryTime,DeliveryTimeId,Description,DescriptionLong,Status,DisableOnEmpty,Discount,DiscountType,Ean,Sorting,MinAmount,Title,Unit")

        # Get all products
        product_return = self.client.service.Product_GetAll()
        products = product_return

        # Loop through products and their variants and print info
        for product in products[-3:]: # First 20 for brevity
          
            
            print(f"product: {product}")
            print("\n==================== Product ====================")
            pprint.pprint(product)
            # Handle StockLocations (nested list)
            if getattr(product.StockLocations, 'item', None):
                print("StockLocations:")
                for stock_loc in product.StockLocations.item:
                    print(f"  Location ID: {getattr(stock_loc, 'StockLocationId', None)}, Stock: {getattr(stock_loc, 'Stock', None)}")
            else:
                print("StockLocations: None")

            # Print Variants if any
            
    def product_get_all_custom_data(self):
        custom_data_types = self.client.service.Product_GetCustomDataAll()
        return custom_data_types
        
        
    def product_get_file(self ):
       file_type = self.client.get_type('ns0:ProductCreateFile')
       print(file_type)       
       return file_type                 

        
        
    def upload_product_picture(self, product_id, image_path, sort=1):
        picture_type = self.client.get_type('ns0:ProductPictureCreate')
        
        picture_data = picture_type(
            ProductId=product_id,
            FileName=image_path,  
            Sorting=sort
        )
        result = self.client.service.Product_CreatePicture(PictureData=picture_data)
        return result
