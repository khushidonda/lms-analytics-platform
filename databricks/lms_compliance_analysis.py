# Databricks notebook source
# MAGIC %md
# MAGIC # Online Learning Engagement Analysis
# MAGIC
# MAGIC Bonus PySpark notebook for the SJSU Data Visualization course project.
# MAGIC Upload CSVs from `data/processed/` to DBFS before running.

# COMMAND ----------

from pyspark.sql import Window
from pyspark.sql import functions as F

# COMMAND ----------

enrollments = spark.read.option("header", True).csv("dbfs:/FileStore/lms/mdl_user_enrolments.csv")
completions = spark.read.option("header", True).csv("dbfs:/FileStore/lms/mdl_course_completions.csv")
users = spark.read.option("header", True).csv("dbfs:/FileStore/lms/mdl_user.csv")
courses = spark.read.option("header", True).csv("dbfs:/FileStore/lms/mdl_course.csv")
enrol = spark.read.option("header", True).csv("dbfs:/FileStore/lms/mdl_enrol.csv")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Join enrollment and completion data

# COMMAND ----------

base = (
    users.alias("u")
    .join(enrollments.alias("ue"), F.col("u.id") == F.col("ue.userid"), "inner")
    .join(enrol.alias("e"), F.col("e.id") == F.col("ue.enrolid"), "inner")
    .join(courses.alias("c"), F.col("c.id") == F.col("e.courseid"), "inner")
    .join(
        completions.alias("cc"),
        (F.col("cc.userid") == F.col("u.id")) & (F.col("cc.course") == F.col("c.id")),
        "left",
    )
    .filter(F.col("u.deleted") == 0)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Compliance summary by department

# COMMAND ----------

summary = (
    base.groupBy("u.department", "c.fullname")
    .agg(
        F.count("*").alias("total_enrolled"),
        F.sum(F.when(F.col("cc.timecompleted").isNotNull(), 1).otherwise(0)).alias("total_completed"),
    )
    .withColumn(
        "completion_rate_pct",
        F.round(F.col("total_completed") / F.col("total_enrolled") * 100, 1),
    )
)

display(summary.orderBy("department", "fullname"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Running total completions with window function

# COMMAND ----------

completed = (
    completions.filter(F.col("timecompleted").isNotNull())
    .withColumn("completion_month", F.date_format(F.from_unixtime("timecompleted"), "yyyy-MM"))
    .join(courses, completions.course == courses.id)
)

window_spec = Window.partitionBy("category").orderBy("completion_month")

trend = (
    completed.groupBy("completion_month", "category")
    .count()
    .withColumnRenamed("count", "completions")
    .withColumn("running_total", F.sum("completions").over(window_spec))
)

display(trend.orderBy("category", "completion_month"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save as Delta table

# COMMAND ----------

summary.write.format("delta").mode("overwrite").saveAsTable("lms_compliance_summary")
print("Saved lms_compliance_summary Delta table")
