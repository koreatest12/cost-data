FROM openjdk:17-alpine
COPY build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
# UPDATED by CI/CD Pipeline
ENV APP_VERSION=2.0.0