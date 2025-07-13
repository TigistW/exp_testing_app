# 🧬 eAMR RAG Evaluation Interface

This Streamlit-based web app enables domain experts to query an eAMR (electronic Antimicrobial Resistance) RAG (Retrieval-Augmented Generation) system, evaluate its responses, and log feedback for quality assurance and model refinement.

---

## 📦 Features

### 🔎 Query & Evaluate (Home Page)
- Choose between two RAG pipelines: `Gemini` or `LLaMA`.
- Input a free-text question related to AMR.
- Automatically fetch relevant documents and a generated summary.
- View a structured summary and raw document content.
- Evaluate the model output using the following metrics:
  - Relevance
  - Factual Accuracy
  - Response Time
  - Perspective Coverage (Human, Animal, Environment)
  - Optional textual comments for each score
- Submit and store evaluations in a local Excel file (`logs/eamr_rag_eval.xlsx`).

### 📊 View Logs (Second Page)
- Visualize all logged evaluations.
- Filter logs by `Examiner` or `Model`.
- Download filtered logs as Excel.

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install streamlit pandas openpyxl requests
````

---

## 🚀 Running the App

1. Clone the repository and navigate to the app directory:

```bash
git clone <your-repo-url>
cd exp_testing_app
```


2. Start the app:

```bash
streamlit run main.py
```

3. Use the sidebar navigation to switch between pages (`Home`, `View_Log`).

---

## 📁 Log File Format

Each evaluation is logged with the following fields:

* Timestamp
* Examiner
* Model
* Query
* Summary
* Relevance (1–10) & Comment
* Factual Accuracy (1–10) & Comment
* Response Time (1–10) & Comment
* Perspective Coverage (1–10) & Comment
* Overall Comment

---

## 🌐 API Configuration

The app sends user queries to these RAG endpoints:

* Gemini: ``
* LLaMA: ``

Each endpoint must accept a POST request with:

```json
{
  "query": "Your question here",
  "n_result": int
}
```

---

## 👤 Authors

* **Tigist Wondimneh Birhan** 

---

## 🧪 Disclaimer

This tool is intended for research and evaluation purposes only. The AI-generated responses do not constitute medical advice.

