# Cost Data - Multi-stage Docker Build
FROM maven:3.9-eclipse-temurin-17-alpine AS build

WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code and build
COPY src ./src
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-alpine

# Install Python for server management tools
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy JAR from build stage
COPY --from=build /app/target/*.jar app.jar

# Copy Python management scripts
COPY server_manager.py .
COPY demo.py .
COPY security_news.py .
COPY requirements.txt .

# Create directories
RUN mkdir -p /app/uploads /app/data /app/DB

# Copy DB files
COPY DB /app/DB

# Expose port 9999
EXPOSE 9999

# Environment variables
ENV SERVER_PORT=9999
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:9999/actuator/health || exit 1

# Run application
CMD ["sh", "-c", "java ${JAVA_OPTS} -Dserver.port=${SERVER_PORT} -jar app.jar"]
