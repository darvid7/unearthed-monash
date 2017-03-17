# Challenge 4

Prove the data can predict stuff

# Setup

1. Frontend webserver w/ graphs 

- heroku + flask

2. Microsoft Azure + SQL server + Machine Learning

# Resources

- Python sklearn on Azure: https://docs.microsoft.com/en-us/azure/machine-learning/machine-learning-execute-python-scripts

- Python datasets on Azure: https://docs.microsoft.com/en-us/azure/machine-learning/machine-learning-python-data-access

- Python dev centre: https://azure.microsoft.com/en-us/develop/python/

- SQL Connections: https://mkleehammer.github.io/pyodbc/

- SQL Connections: https://docs.microsoft.com/en-us/azure/sql-database/sql-database-develop-python-simple

# Steps:

1. Set up Flask on Azure [done]

2. Query SQL DB [done]

3. Work on ML model [doing]

4. Run hope it works

5. Fancy front end stuff

# DB Connection

teammonash

qwer1234!

# How to set stuff up notes

## SQL 

https://portal.azure.com/#resource/subscriptions/f9e8fbb0-ed0e-4a31-9344-740f2b1f639e/resourceGroups/hackathon/providers/Microsoft.Sql/servers/unearthed/databases/myDatabase/overview

1. go to database on Azure

2. Click on tools on the top

3. Query Editor

4. Run queries 

- find all tabes in sql db. 
SELECT * FROM SYS.TABLES;

- get all data from a table (represents a csv sheet)
SELECT * FROM [13Blasthole XRF];

## ML Model

https://studio.azureml.net/Home/ViewWorkspaceCached/0dc872b4ef8c463c9f34086f091ce222#Workspaces/Experiments/Experiment/0dc872b4ef8c463c9f34086f091ce222.f-id.84e9c3b6a5b64499aa7a502290e51dcc/ViewExperiment

1. drag Data Input and Output

- data source = Azure SQL DB

- server = unearthed.database.windows.net

- database name = myDatabase

- teamname = teammonash

- pw = qwer1234!

set db query = your query i.e. SELECT * FROM [13Blasthole XRF];

2. Mess around with model things to make algo

3. Delpoy web service

4. Configure and get API key, can query this (it is a REST API) 
