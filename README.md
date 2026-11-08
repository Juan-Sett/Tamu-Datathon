# Aggie Decision Desk

Aggie Decision Desk is a data-grounded campus planning copilot for the Best Use of Snowflake API challenge.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app works immediately in demo mode. To use live Snowflake data:

1. Run `snowflake_setup.sql` in Snowsight.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
3. Fill in the Snowflake account, host, and PAT.
4. Restart Streamlit and enable “Use Snowflake live data.”

Never commit `.streamlit/secrets.toml` or expose the PAT in frontend code.

## Deploy

Deploy this repository as a Streamlit service on Render with the start command:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

Add the Snowflake values as deployment environment secrets or Streamlit secrets, then point your GoDaddy DNS record at the hosted service.

Recommended domain layout:

- `jaunes.us` — future portfolio website
- `www.jaunes.us` — optional portfolio alias
- `aggie.jaunes.us` — Aggie Decision Desk app
