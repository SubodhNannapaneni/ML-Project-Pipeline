import os
import sys
from source.exceptions import CustomException
from source.logger import logging
import pandas as  pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass

from source.components.data_transformation import DataTransformation
from source.components.data_transformation import DataTransformationConfig

from source.components.model_trainer import ModelTrainer, ModelTrainerConfig

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

# authenticate
credential = DefaultAzureCredential()

# Get a handle to the workspace
ml_client = MLClient(
    credential=credential,
    subscription_id="bc762a7b-5275-4651-8fab-5857d882a7ed",
    resource_group_name="fevtutorAI-dev",
    workspace_name="ws_ai_dev",
)



@dataclass
class DataIngestionConfig:
    train_data_path:str = os.path.join('data', 'train.csv')
    test_data_path:str = os.path.join('data', 'test.csv')
    raw_data_path:str = os.path.join('data', 'raw_data.csv')
    
class DataIngestion:
    def __init__(self):
        self.ingestion_config =DataIngestionConfig()
        
    def initiate_data_ingestion(self):
        logging.info('Starting data ingestion...')
        try:
            # data_asset = ml_client.data.get(name="StudentsPerformance", version=1)
            # df = pd.read_csv(data_asset.path)
            df = pd.read_csv('data\StudentsPerformance.csv')
            logging.info('read the data as df')
            
            # move math score column to the end
            math_score_col = df.pop('math score')
            df['math score'] = math_score_col
            
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path),exist_ok=True)
            
            df.to_csv(self.ingestion_config.raw_data_path, index=False,header=True)
            logging.info('train-test split initiated')
            train_set, test_set = train_test_split(df,test_size=0.2, random_state=1)
            
            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header= True)
            
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header= True)
            
            logging.info("Ingestion of data is completed.")
            
            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
                
        except Exception as e:
            raise CustomException(e, sys)
        
if __name__ == '__main__':
    obj = DataIngestion()
    train_data, test_data = obj.initiate_data_ingestion()
    
    data_transformation = DataTransformation()
    train_arr, test_arr,_ = data_transformation.initiate_data_transformations(train_data, test_data)
    
    model_trainer = ModelTrainer()
    print(model_trainer.initiate_model_trainer(train_arr, test_arr))