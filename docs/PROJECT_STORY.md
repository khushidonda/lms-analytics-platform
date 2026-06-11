# Project Story — How This Started

## The assignment

In my **Data Visualization** graduate course at San Jose State University, our professor asked us to build an interactive dashboard in **Power BI** using a real-world dataset. The goal was to practice data cleaning, SQL-style thinking, and visual storytelling — not just making charts.

## Finding a dataset

I searched Kaggle and Google Dataset Search for something with enough rows to analyze and enough dimensions to visualize. I landed on public **online learning / employee training** datasets (similar to [HR Analytics: Employee Training & Development](https://www.kaggle.com/datasets/rabieelkharoua/hr-analytics-employee-training-and-development) and [Online Learning Platform](https://www.kaggle.com/datasets/khaledatef1/online-learning-platform)).

The fields looked familiar: user ID, course name, enrollment date, completion status, department/program. That led me to read about **Learning Management Systems (LMS)** — platforms like Moodle and Canvas that universities use to host online courses.

## What I built (medium scope)

I did **not** try to replicate a full corporate LMS rollout. Instead I built a **course-sized analytics project**:

1. **Python** — cleaned and extended the dataset idea into ~120 graduate students across 4 SJSU-style programs and 6 online courses
2. **SQL** — wrote queries for enrollment summaries, incomplete courses, and monthly trends
3. **Power BI** — main deliverable: 3-page dashboard for the class
4. **Moodle (optional)** — spun up a local Docker instance to see what LMS data actually looks like in the database
5. **Databricks (bonus)** — explored the same data in PySpark for practice

## What this is NOT

- Not a copy of any company's internal LMS operations
- Not a full enterprise compliance platform
- Not interview-specific work — it's a **graduate school data visualization project** that happens to use SQL, Power BI, Python, and LMS concepts

## Tech stack (aligned with coursework + resume skills)

| Tool | How I used it |
|------|----------------|
| Power BI | Primary dashboard deliverable |
| SQL | Data prep and analysis queries |
| Python / Pandas | Dataset generation and validation |
| Excel / CSV | Intermediate exports for Power BI |
| Moodle | Explored open-source LMS data model locally |
| Databricks | Optional notebook for aggregation practice |
