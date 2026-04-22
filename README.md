# Tool Test SQA - CVConnect Authentication

This repository contains the automated API tests for the CVConnect Authentication module, implemented using Postman and Newman.

## Contents
- **`CVConnect_Auth_API_Test.postman_collection.json`**: The complete Postman Collection containing 20 Test Cases covering Login, Registration, Token Verification, Email Verification, and Password Reset.
- **`Tool_Test_Postman_PhanAnh.xlsx`**: The formal Software Quality Assurance (SQA) execution matrix, mapping the Postman tests to documented Test Cases.
- **`generate_excel.py`**: A Python script to auto-generate the Excel report.

## How to Run

1. Import the `CVConnect_Auth_API_Test.postman_collection.json` into Postman.
2. Ensure the `cvconnect-user-service` is running locally on port 8080.
3. Click "Run" on the collection. No manual variables are required; everything is handled via collection variables.

### Prerequisites
- Node.js & npm (for Newman)
- `npm install -g newman`

Run tests via CLI:
```bash
newman run CVConnect_Auth_API_Test.postman_collection.json
```
