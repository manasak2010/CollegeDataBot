# CollegeDataBot

CollegeDataBot is a Streamlit RAG assistant for asking questions over college information stored in CSV files. It chunks uploaded CSV content, builds a FAISS vector index with Google Gemini embeddings, and answers questions with a Gemini chat model using retrieved context.

## What This Project Contains

- `app1.py` - main Streamlit RAG assistant
- `bot/first.py` - optional scraper and extractive QA demo
- `sample_data/griet_sample.csv` - small sample college-information CSV
- `.env.example` - environment variable template
- `requirements.txt` - Python dependencies

## Setup

```bash
git clone https://github.com/manasak2010/CollegeDataBot.git
cd CollegeDataBot

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Create a local `.env` file and add your Google API key:

```bash
copy .env.example .env
```

Then edit `.env`:

```text
GOOGLE_API_KEY=your_google_api_key_here
```

## Run

```bash
streamlit run app1.py
```

Upload a CSV file, click **Submit & Process**, then ask questions about the uploaded content.

## Notes

- `.env` and Streamlit secrets files are intentionally ignored.
- `faiss_index/` is generated locally after processing a CSV and should not be committed.
- Large scraped CSVs, notebooks, trained model outputs, and third-party package copies are excluded from this repository.
