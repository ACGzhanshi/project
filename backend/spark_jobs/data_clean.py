"""Spark数据清洗任务"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, trim, upper, avg, count, min as spark_min, max as spark_max
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType


def get_spark_session():
    """获取Spark会话"""
    return SparkSession.builder \
        .appName("GaokaoZhiyuan") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()


def clean_score_data(raw_data_list):
    """清洗分数线数据"""
    spark = get_spark_session()

    schema = StructType([
        StructField("university_name", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("province", StringType(), True),
        StructField("subject_type", StringType(), True),
        StructField("min_score", IntegerType(), True),
        StructField("max_score", IntegerType(), True),
        StructField("avg_score", IntegerType(), True),
    ])

    df = spark.createDataFrame(raw_data_list, schema)

    cleaned_df = df \
        .filter(col("min_score").isNotNull()) \
        .filter(col("min_score") > 0) \
        .filter(col("min_score") <= 750) \
        .withColumn("university_name", trim(col("university_name"))) \
        .withColumn("province", trim(col("province"))) \
        .dropDuplicates(["university_name", "year", "province", "subject_type"])

    result = cleaned_df.collect()
    spark.stop()
    return [row.asDict() for row in result]


def analyze_score_trends(score_data_list):
    """分析分数线趋势"""
    spark = get_spark_session()

    schema = StructType([
        StructField("university_name", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("province", StringType(), True),
        StructField("subject_type", StringType(), True),
        StructField("min_score", IntegerType(), True),
    ])

    df = spark.createDataFrame(score_data_list, schema)

    trend_df = df.groupBy("university_name", "province", "subject_type") \
        .agg(
            avg("min_score").alias("avg_min_score"),
            spark_min("min_score").alias("lowest_score"),
            spark_max("min_score").alias("highest_score"),
            count("*").alias("year_count")
        )

    result = trend_df.collect()
    spark.stop()
    return [row.asDict() for row in result]


def build_recommendation_features(score_data_list):
    """构建推荐模型特征"""
    spark = get_spark_session()

    schema = StructType([
        StructField("university_name", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("province", StringType(), True),
        StructField("min_score", IntegerType(), True),
        StructField("min_rank", IntegerType(), True),
    ])

    df = spark.createDataFrame(score_data_list, schema)

    features_df = df.groupBy("university_name", "province") \
        .agg(
            avg("min_score").alias("avg_score"),
            avg("min_rank").alias("avg_rank"),
            count("*").alias("data_years"),
        ) \
        .filter(col("data_years") >= 2)

    result = features_df.collect()
    spark.stop()
    return [row.asDict() for row in result]
