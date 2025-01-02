# Prerequisites

Python should come with pip installed, to upgrade

```cmd
python -m pip install --upgrade pip
```

# Set up a Virtual Environment (recommended)
From inside the repo execute
## For Windows
```
python -m venv .venv
venv\Scripts\activate
```
## For Mac/Linux
```
python3 -m venv .venv
source venv/bin/activate
```
# Install Dependencies
Use pip to install the required libraries:
```
pip install -r requirements.txt
```
# Start the FastAPI development server using uvicorn:

```
uvicorn main:app --reload
```
This will run the FastAPI server on http://127.0.0.1:8000/ by default.

OpenAPI documentation at http://127.0.0.1:8000/docs
