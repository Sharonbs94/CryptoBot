FROM python:3.9-buster

# Install OpenJDK 11 Headless and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless wget curl gnupg2 && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:${PATH}"

# Install PySpark and dependencies
RUN pip install pyspark==3.5.2 kafka-python requests

# Create the jars directory
RUN mkdir -p /opt/spark/jars/

# Download the necessary Spark Kafka packages
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.2/spark-sql-kafka-0-10_2.12-3.5.2.jar -P /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.2/spark-token-provider-kafka-0-10_2.12-3.5.2.jar -P /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar -P /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar -P /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar -P /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.10.5/snappy-java-1.1.10.5.jar -P /opt/spark/jars/

# Verify JAR files
RUN ls -l /opt/spark/jars/

# Set the working directory inside the container
WORKDIR /app

# Copy application code
COPY core/ /app/core/
COPY utils/ /app/utils/
COPY config/ /app/config/
COPY requirements.txt /app/
COPY handlers/ /app/handlers/
COPY bot_setup.py /app/
COPY main.py /app/main.py

# Install any Python dependencies
RUN pip install -r requirements.txt