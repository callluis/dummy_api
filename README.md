# DUMMY API
Just a dummy API to have a class about APIs.

## Installation
1. Install [`Python 3.7`](https://realpython.com/installing-python/) or higher.  
2. Install required python modules with the command: `pip install -r requirements.txt`.

## Execution
1. `cd` using the terminal to the root folder of the project.
2. Run command `gunicorn main:application --bind 127.0.0.1:8100` 
3. Start sending [requests](./collection) to the API.

## Execution (only to debug)
Run command `gunicorn main:application --bind 127.0.0.1:8100 --reload --timeout 500` instead.
