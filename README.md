**AI-Based Data Analytics for CRM Optimization: Driving Car Sales Success**

<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/ee76088b-4c9f-4ad7-91d0-8788afc69947" />
<img width="1920" height="1021" alt="3" src="https://github.com/user-attachments/assets/94e685ca-1509-4c17-bf31-48f3d5473a14" />

**Sponsored by: Group Landmark Ltd., Mumbai**
Program: B.E. Information Technology, Semester VIII (Major Project), AY 2025–26
Institute: Finolex Academy of Management and Technology, Ratnagiri (Affiliated to University of Mumbai)

**Overview**

Car dealerships collect large volumes of CRM data (call logs, lead details, test-drive records), but most of it stays unused. Tracking is often manual, which is slow and leads to lost sales opportunities.

This project is a web application that takes a dealership's CRM exports and runs an automated analytics pipeline (data loading → cleaning → EDA → machine learning). It then presents the results as interactive dashboards. Optional AI-generated written insights can be added using the Claude API.

**Objectives**

Collect, clean and preprocess CRM datasets for analytics.
Apply ML models to derive insights on agent performance and lead conversion.
Build a dashboard / web application to visualize customer connectivity trends.
Help managers prioritize leads and improve agent productivity.


<img width="1920" height="1080" alt="4" src="https://github.com/user-attachments/assets/3bcff8f8-127d-4555-a624-e796005ea0da" />
<img width="1920" height="1080" alt="6" src="https://github.com/user-attachments/assets/b6ea3665-ebdf-40f7-8807-9afb97209d8a" />
<img width="1920" height="1080" alt="7" src="https://github.com/user-attachments/assets/33953605-4d80-4c10-a807-bff549b0362e" />
<img width="1920" height="1080" alt="10" src="https://github.com/user-attachments/assets/467a365e-efe0-4fa0-b9c8-01d8025d94c0" />
<img width="1920" height="1080" alt="13" src="https://github.com/user-attachments/assets/fe013d5c-52ab-4778-95f7-8e5ce3c888b1" />

**System Workflow**

```text
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
```


**Tech Stack**
Language: Python
Data & ML: Pandas, NumPy, scikit-learn
Visualization: Plotly
Web app: Streamlit
AI insights (optional): Anthropic API
In progress: FastAPI backend + React frontend (backend/, frontend/)

**Project Structure**
```
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
```
**Getting Started**
1. Clone the repository
bash
git clone https://github.com/Anuja57/car-sales-crm-analytics.git
cd car-sales-crm-analytics
2. Create a virtual environment and install dependencies
bash
python -m venv venv
venv\Scripts\activate         
source venv/bin/activate    
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

**Data Note**

The dataset comes from the sponsoring company and is used for academic purposes only. Raw company data is not included in this repository. To try the app, use your own CSV exports with the same column structure.

**Sample Results (on the project dataset)**
1,000 leads analysed, with an 80.4% conversion rate and 12 high-potential unconverted leads identified.
592 unique customers profiled, with an average callback rate of 85.8%.
Agents ranked into High / Medium / Low tiers using clustering and a weighted score.
Random Forest feature importance showed lead source and lead age as the strongest drivers of conversion.

**Future Scope**
Complete the React + FastAPI version for deployment.
Extend to other industries such as BPO, banking and retail.
Real-time dashboards and alerts for managers.
Validate the models on larger datasets.

**SDG Alignment**
SDG 9: Industry, Innovation and Infrastructure
SDG 8: Decent Work and Economic Growth

**Team** 
Yukta Bhujbal	
Anuja Gadekar	
Vaishnavi Pokale	

**Guides:** Prof. Onkar Dike (Assistant Professor) and Mr. Bhushan Kharare (Senior Data Analyst)

**Acknowledgements**

Group Landmark Ltd., Mumbai, for sponsoring the project, and Finolex Academy of Management and Technology, Ratnagiri.
