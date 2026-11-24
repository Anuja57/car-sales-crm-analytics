AI-Based Data Analytics for CRM Optimization: Driving Car Sales Success
<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/ee76088b-4c9f-4ad7-91d0-8788afc69947" />
<img width="1920" height="1080" alt="3" src="https://github.com/user-attachments/assets/6fc502b1-dfc7-4a94-9482-e6350ac38452" />
Sponsored by: Group Landmark Ltd., Mumbai
Program: B.E. Information Technology, Semester VIII (Major Project), AY 2025–26
Institute: Finolex Academy of Management and Technology, Ratnagiri (Affiliated to University of Mumbai)

Overview

Car dealerships collect large volumes of CRM data (call logs, lead details, test-drive records), but most of it stays unused. Tracking is often manual, which is slow and leads to lost sales opportunities.

This project is a web application that takes a dealership's CRM exports and runs an automated analytics pipeline (data loading → cleaning → EDA → machine learning). It then presents the results as interactive dashboards. Optional AI-generated written insights can be added using the Claude API.

Objectives
Collect, clean and preprocess CRM datasets for analytics.
Apply ML models to derive insights on agent performance and lead conversion.
Build a dashboard / web application to visualize customer connectivity trends.
Help managers prioritize leads and improve agent productivity.
Features
Module	What it does	Method
Agent Performance	Ranks agents on calls, hot-lead ratio, callbacks and test drives, and groups them into High / Medium / Low tiers	K-Means (k=3) + weighted composite score
Customer Connectivity	Scores customer engagement and shows call trends, location and car-model interest	Rule-based engagement score (calls, callback rate, lead type)
Lead Conversion	Predicts each lead's conversion probability and lists high-potential unconverted leads	Random Forest (150 trees, balanced class weights)
EDA Summary	Data quality overview: rows, columns, duplicates and missing values per file	Pandas
AI Insights (optional)	Plain-English summary of each dashboard	Claude API
Screenshots

Replace the file names below with your own screenshot names in the screenshots/ folder.

Agent Performance	Customer Connectivity
Agent Performance	Customer Connectivity
Lead Conversion	ML Feature Importance
Lead Conversion	Feature Importance
System Workflow
CRM CSV files (leads, calls, test drives)
        │
        ▼
Data loading → Cleaning → EDA
        │
        ▼
ML analysis (K-Means / rule-based scoring / Random Forest)
        │
        ▼
Interactive Plotly dashboards in Streamlit  (+ optional AI insights)
Tech Stack
Language: Python
Data & ML: Pandas, NumPy, scikit-learn
Visualization: Plotly
Web app: Streamlit
AI insights (optional): Anthropic API
In progress: FastAPI backend + React frontend (backend/, frontend/)
Project Structure
├── app.py                  # Streamlit entry point
├── pipeline/
│   ├── data_loader.py      # Loads the CSV files
│   ├── data_cleaner.py     # Cleaning and EDA summaries
│   ├── ml_engine.py        # K-Means, scoring and Random Forest
│   └── ai_insights.py      # Optional AI-generated insights
├── dashboards/
│   ├── agent_performance.py
│   ├── customer_connectivity.py
│   └── lead_conversion.py
├── utils/helpers.py        # ID-to-label mappings and helpers
├── backend/                # FastAPI version (in progress)
├── frontend/               # React version (in progress)
├── screenshots/
├── requirements.txt
└── .env.example
Getting Started
1. Clone the repository
bash
git clone https://github.com/Anuja57/car-sales-crm-analytics.git
cd car-sales-crm-analytics
2. Create a virtual environment and install dependencies
bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
3. Run the app
bash
streamlit run app.py

The app opens at http://localhost:8501.

4. Use the app
Upload the three CSV files in the sidebar: leads.csv, sales_completed_calls.csv, sales_test_drive_details.csv.
Click Run Analysis.
Explore the tabs: Agent Performance, Customer Connectivity, Lead Conversion, EDA Summary.
Optional: AI insights

Copy .env.example to .env and set your key:

ANTHROPIC_API_KEY=your_key_here

The app works fully without it.

Data Note

The dataset comes from the sponsoring company and is used for academic purposes only. Raw company data is not included in this repository. To try the app, use your own CSV exports with the same column structure.

Sample Results (on the project dataset)
1,000 leads analysed, with an 80.4% conversion rate and 12 high-potential unconverted leads identified.
592 unique customers profiled, with an average callback rate of 85.8%.
Agents ranked into High / Medium / Low tiers using clustering and a weighted score.
Random Forest feature importance showed lead source and lead age as the strongest drivers of conversion.
Future Scope
Complete the React + FastAPI version for deployment.
Extend to other industries such as BPO, banking and retail.
Real-time dashboards and alerts for managers.
Validate the models on larger datasets.
SDG Alignment
SDG 9: Industry, Innovation and Infrastructure
SDG 8: Decent Work and Economic Growth
Team (Group 03)
Name	Registration No.
Yukta Bhujbal	T-22-0525
Anuja Gadekar	T-22-0516
Vaishnavi Pokale	T-22-0022

Guides: Prof. Onkar Dike (Assistant Professor) and Mr. Bhushan Kharare (Senior Data Analyst)

Acknowledgements

Group Landmark Ltd., Mumbai, for sponsoring the project, and Finolex Academy of Management and Technology, Ratnagiri.
