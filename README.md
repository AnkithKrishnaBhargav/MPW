# NSW Carbon Allocation

Run locally:

1. Create virtualenv & install:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Ensure CSV `api/assets/Extracted_Dataset - Sheet1.csv` exists.

3. Run:
    If on cmd prompt:
        ./run.sh
    
    Powershell:
    terminal 1:
        ```
        python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
        ```
    terminal 2:
     ```
        python -m http.server 3000 --directory frontend
     ```

4. Open http://localhost:3000 (static frontend) and click Refresh.

API endpoints:
- GET /                 -> health
- POST /allocate        -> run allocation with JSON payload
- GET /allocate-from-csv?path=... -> convenience endpoint that loads CSV and runs allocation
