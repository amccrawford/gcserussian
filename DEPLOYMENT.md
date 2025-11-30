# Deployment Guide: Streamlit Community Cloud + Neon (Free Tier)

This guide explains how to deploy your GCSE Russian Practice App for free.

## Step 1: Get a Free Database
We need a database that lives in the cloud, not on your computer.

1.  Go to **[Neon.tech](https://neon.tech/)** and sign up.
2.  Create a **New Project** (e.g., "gcse-russian-app").
3.  Once created, look for the **Connection String** on the dashboard.
4.  It will look like: `postgres://user:password@ep-xyz.Region.neon.tech/neondb...`
5.  **Copy this string.** You will need it for Step 3.

## Step 2: Push Code to GitHub
Streamlit deploys directly from GitHub.

1.  Make sure all your latest changes are committed and pushed to your GitHub repository.
    *   `git add .`
    *   `git commit -m "Ready for deployment"`
    *   `git push origin master`

## Step 3: Deploy to Streamlit Cloud

1.  Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
2.  Click **"New app"**.
3.  Select your **GitHub Repository**, **Branch** (`master`), and **Main file path** (`streamlit_app.py`).
4.  **IMPORTANT: Advanced Settings (Secrets)**
    *   Click "Advanced Settings" before hitting Deploy.
    *   You need to add your API keys here in the "Secrets" format (TOML).
    *   Paste the following into the secrets box, replacing the values with your real keys:

    ```toml
    GEMINI_API_KEY = "your_google_gemini_key_here"
    DATABASE_URL = "your_neon_connection_string_here" 
    ```
    *(Note: Paste the Neon connection string you copied in Step 1).*

5.  Click **"Deploy!"**.

## Step 4: Initialize the Database
On the first run, the cloud database will be empty (no tables, no users).

1.  Once the app is live (you see the URL), the app might crash or error because users don't exist yet.
2.  **One-time Setup:** We need to run the seeding script.
    *   Since we can't easily run shell commands on Streamlit Cloud, the app will auto-create tables (thanks to `database.py`).
    *   However, the *users* won't exist.
    *   **Quick Fix:** I have added a secret "Admin Init" button to the login page logic (hidden or triggered via a specific URL parameter) OR you can connect to your Neon database using a tool like **DBeaver** or **TablePlus** on your laptop using that same connection string and run the SQL to insert the users manually.

    **SQL to run manually in Neon's SQL Editor (on their website):**
    ```sql
    -- You can generate the hashed passwords using python locally:
    -- import auth_utils; print(auth_utils.get_password_hash("password123"))
    
    INSERT INTO users (username, hashed_password, role) VALUES 
    ('student1', '$2b$12$....(your_hashed_password)...', 'student');
    ```

## Troubleshooting
*   **Audio:** If recording doesn't work, check your browser permissions. Note that some browsers block audio on HTTP, but Streamlit Cloud provides HTTPS automatically, so it should work.
