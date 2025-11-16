# **ausjdocs-analysis**

This repository contains a small data exploration and qualitative analysis project examining discussions related to pharmacists within the **r/ausjdocs** subreddit.
The goal is to extract, review, and summarise themes from posts and comments that reference hospital pharmacy practice, pharmacist–doctor interactions, and medication-related issues raised by junior doctors.

---

## **Project Overview**

The workflow consists of:

### **1. Data Collection (Reddit Scraping)**

Python scripts (`reddit_scraper.py`, `comment_scraper.py`) were used to:

* Retrieve posts and comments from r/ausjdocs containing pharmacy-related keywords
* Save raw content into structured JSON files for analysis
* Avoid any personal identifiers (usernames, IDs), focusing only on text content

Data files:

* `ausjdocs_pharmacy_posts.json`
* `hospital_pharmacy_comments.json`

### **2. Qualitative Review**

The extracted text was manually reviewed to identify recurring themes such as:

* Experiences with hospital pharmacists
* Points of friction or misunderstanding
* Safety-net contributions pharmacists provide
* Specialty-specific prescribing complexities
* Perceived educational gaps and communication patterns
  (Themes summarised in the accompanying HTML output.)

### **3. HTML Output**

`index.html` and `style.css` contain a formatted presentation of the qualitative findings, including:

* Representative quotes
* Neutral interpretive commentary
* Observed patterns and contextual limitations

This is intended as an informational / reflective piece rather than an academic publication.

---

## **Limitations**

* Reddit users are heterogeneous (junior doctors, senior doctors, and allied health), limiting generalisability.
* Findings represent opinions expressed online, not verified practice patterns.
* Jurisdictional differences in medicines legislation and pharmacy practice across Australian states may limit applicability.
* The dataset reflects a snapshot in time, not the full breadth of pharmacist-doctor interactions.

---

## **Repository Structure**

```
.
├── index.html                # Main HTML output (renamed for Netlify)
├── style.css                 # Dark-mode friendly stylesheet
├── reddit_scraper.py         # Script for collecting initial post data
├── comment_scraper.py        # Script for collecting comment trees
├── ausjdocs_pharmacy_posts.json
├── hospital_pharmacy_comments.json
└── README.md                 # (This file)
```

## **Purpose**

This project is mainly exploratory — intended as a reflective resource for:

* Understanding how pharmacists are perceived in online medical communities
* Identifying communication patterns and misconceptions
* Providing junior pharmacists or trainees insight into common themes discussed by junior doctors
* Supporting ongoing education and practice improvement

* A more academic version
* A GitHub Pages version instead of Netlify
* A project logo/banner
* A contributors / licence section (MIT, Apache, etc.)
