# 🐠 Torani-Machine Learning Codebase 🧠

This repository is used to store all of the codes related to the development of the machine learning side of Fishku's Seller App. 📲

## Description 📝
There are several folders that separate each file into their corresponding purpose. These folders are organized with the intention of documenting purposes, not for executing purposes. For example, the cloud functions need another platform to be executed, which is Cloud Run in Google Cloud Platform, and this repository is only used to store the codebase. 💻

Below are the descriptions of each folder. 📂

* **cloud-functions** 🌩️  
This is a Cloud Function that creates and runs an ARIMA_PLUS model on BigQuery ML. It also stores the prediction data on Cloud Storage Bucket. The function is triggered by a Cloud Scheduler job that runs weekly. The function consists of two files: main.py and requirements.txt.
    * **main.py**: This file contains the code for the Cloud Function that scrapes, cleans, and processes the data from the web, creates and runs an ARIMA_PLUS model on BigQuery ML, and stores the prediction data on Cloud Storage Bucket. It uses helper functions and modules to perform various tasks and queries.
    * **requirements.txt**: This file contains the list of dependencies for the Cloud Function. It specifies the modules and libraries that are needed to run the code in main.py. It includes requests, pandas, numpy, google-cloud-bigquery, and google-cloud-storage.

* **notebooks** 📓  
We used 3 different notebooks which serve to fulfill 2 different functionalities: data scrape and fish's price prediction functionality.
    * **data-scrape** 🎣  
    This notebook is used to scrape the fish's price data from PDSPKP's Data Center and retrieve it in a CSV format. We used the BeautifulSoup framework to parse the HTML content inside the web page. We also used pandas and numpy to apply some data preprocessing steps to clean our retrieved dataset.
    * **price-prediction** 💰  
    These noteboks are used for developing the machine learning model of fish price prediction. The model that developed is LSTM and RNN utilizing TensorFlow and can be found in **fish_price_prediction.ipynb**. The LSTM model is chosen and the model for predicting five fishes price is further developed in **multiple_fish_price_prediction.ipynb**.
* **saved-models** 💾  
There are five saved models saved in H5 format. These five models represent the price prediction models for each breed that are sold across the Jakarta region. The reason behind the limited number of fish breeds is the scarcity of datasets regarding this fish's price prediction problem.
