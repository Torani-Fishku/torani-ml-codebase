# Torani-Machine Learning Codebase

This repository is used to store all of the codes related to development of machine learning side of Fishku's Seller App.

## Description
There are several folders that separate each files into their corresponding purpose. These folders are organized with the intention of documenting purposes, not for executing purposes. For example, the cloud functions need another platform to be executed, which is Cloud Run in Google Cloud Platform and this repository only used to store the codebase.

Below are the descriptions of each folder.

* **cloud-functions**

* **notebooks**  
We used 3 different notebooks which serve to fulfill 2 different functionalities, data scrape and fish's price prediction functionality.
    * **data-scrape**  
    This notebook is used to scrape the fish's price data from PDSPKP's Data Center and retrieve it in a csv format. We used BeautifulSoup framework to parse the HTML content inside the web page. We also used pandas and numpy to apply some data pre-processing steps to clean our retrieved dataset.
    * **price-prediction**
* **saved-models**
