import boto3
import pandas as pd
import streamlit as st
import json
import requests

class Data:
    def __init__(self):
        self.aws_access_key_id = st.secrets["aws_access_key_id"]
        self.aws_secret_access_key = st.secrets["aws_secret_access_key"]
        self.aws_bucket_name = st.secrets["aws_bucket_name"]
        self.aws_validator_file_name = st.secrets["aws_validator_file_name"]
        self.aws_staking_rate_file_name = st.secrets["aws_staking_rate_file_name"]
        self.aws_eth_supply_file_name = st.secrets["aws_eth_supply_file_name"]
        self.aws_l2_transactions_file_name = st.secrets["aws_l2_transactions_file_name"]
        self.aws_l2_users_file_name = st.secrets["aws_l2_users_file_name"]
        self.region_name = st.secrets["region_name"]
        
        self.s3 = boto3.client('s3',
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key,
                            region_name=self.region_name)
        self.bucket_name = self.aws_bucket_name
        self.file_name = self.aws_validator_file_name
        
        self.scaling = [0, 327680, 393216, 458752, 524288, 589824, 655360, 720896, 786432, 851968, 917504, 983040, 1048576, 1114112, 1179648, 1245184, 1310720, 1376256, 1441792, 1507328, 1572864, 1638400, 1703936, 1769472, 1835008, 1900544, 1966080, 2031616, 2097152, 2162688, 2228224, 2293760, 2359296, 2424832, 2490368, 2555904, 2621440, 2686976, 2752512]
        self.epoch_churn = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42]
        self.day_churn = [1000, 1125, 1350, 1575, 1800, 2025, 2250, 2475, 2700, 2925, 3150, 3375, 3600, 3825, 4050, 4275, 4500, 4725, 4950, 5175, 5400, 5625, 5850, 6075, 6300, 6525, 6750, 6975, 7200, 7425, 7650, 7875, 8100, 8325, 8550, 8775, 9000, 9225, 9450]

    def fetch_json_data(self):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=self.file_name)
            json_data = response['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            return data
        except Exception as e:
            st.error(f"Error retrieving JSON file from S3: {e}")
            return None

    def fetchEntryWait(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'entry_wait']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None

    def fetchExitWait(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'exit_wait']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None

    def fetchValidatorsAndChurn(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'validators']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')

            churn_values = []
            for _, row in df.iterrows():
                validators = row['validators']
                for i in range(len(self.scaling)):
                    if validators <= self.scaling[i]:
                        churn_values.append(self.epoch_churn[i])
                        break

            df['churn'] = churn_values
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None

    # For the bar chart
    def fetchStakingAPY(self):
        try:
            s3 = boto3.client('s3',
                            aws_access_key_id=st.secrets["aws_access_key_id"],
                            aws_secret_access_key=st.secrets["aws_secret_access_key"],
                            region_name=st.secrets["region_name"])
            bucket_name = st.secrets["aws_bucket_name"]
            aws_staking_rate_file_name = st.secrets["aws_staking_rate_file_name"]
            
            response = s3.get_object(Bucket=bucket_name, Key=self.aws_staking_rate_file_name)
            json_data = response['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"Error retrieving staking APY data from S3: {e}")
            return None
        
    # For the header
    def fetchAPR(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'apr']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None

    def fetchStakedAmount(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'staked_amount', 'staked_percent']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None

    def fetchEntryQueue(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'entry_queue']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None

    def fetchExitQueue(self):
        try:
            data = self.fetch_json_data()
            df = pd.DataFrame(data)
            df = df[['date', 'exit_queue']]
            df.rename(columns={'date': 'Date'}, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            return df
        except Exception as e:
            st.error(f"General Error: {e}")
            return None
        
    def fetchEthSupplyData(self):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=self.aws_eth_supply_file_name)
            json_data = response['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            df = pd.DataFrame(data)
            df['Time'] = pd.to_datetime(df['Time'])
            df = df.sort_values('Time')
            return df
        except Exception as e:
            st.error(f"Error retrieving ETH supply data from S3: {e}")
            return None

    def fetchEthereumL2Data(self):
        try:
            response_transactions = self.s3.get_object(Bucket=self.bucket_name, Key=self.aws_l2_transactions_file_name)
            json_data_transactions = response_transactions['Body'].read().decode('utf-8')
            data_transactions = json.loads(json_data_transactions)
            df_transactions = pd.DataFrame(data_transactions['result']['rows'])
            df_transactions['date'] = pd.to_datetime(df_transactions['date'])
            df_transactions = df_transactions.sort_values('date')

            response_users = self.s3.get_object(Bucket=self.bucket_name, Key=self.aws_l2_users_file_name)
            json_data_users = response_users['Body'].read().decode('utf-8')
            data_users = json.loads(json_data_users)
            df_users = pd.DataFrame(data_users['result']['rows'])
            df_users['date'] = pd.to_datetime(df_users['date'])
            df_users = df_users.sort_values('date')

            df_transactions_detailed = df_transactions.copy()

            return df_transactions, df_users, df_transactions_detailed
        except Exception as e:
            st.error(f"Error retrieving Ethereum L2 data from S3: {e}")
            return None, None, None