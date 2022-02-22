import base64 
from google.cloud import storage
import os

class ImageSave():
    def __init__(self,item_id,base64Data,data_type):
        self.item_id = item_id
        self.base64Data = base64Data
        self.data_type = data_type
        
    def ImageSave(self):
        if 'base64' in self.base64Data:
            img = self.base64Data.split(',')[1]
            img_type = self.base64Data.split(',')[0].split('/')[1].split(';')[0]
            img_data = base64.b64decode(img)
            # 生成图片
            with open(f'image/{self.data_type}/{self.item_id}.{img_type}', 'wb') as f:
                f.write(img_data)
            storage_client = storage.Client.from_service_account_json('sport168-data-116c55d4e1bd.json')
            bucket = storage_client.bucket('sport168-image')
            blob = bucket.blob(f'image/{self.data_type}/{self.item_id}')
            blob.upload_from_filename(f'image/{self.data_type}/{self.item_id}.{img_type}')
            os.remove(f'image/{self.data_type}/{self.item_id}.{img_type}')
            return f'https://storage.googleapis.com/sport168-image/image/{self.data_type}/{self.item_id}'
        else:
            return self.base64Data