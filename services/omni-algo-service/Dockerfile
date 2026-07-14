FROM eclipse-temurin:25-jre-jammy AS builder
WORKDIR /app
COPY target/*.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract
FROM eclipse-temurin:25-jre-jammy
RUN groupadd -r omni && useradd -r -g omni omni
USER omni
WORKDIR /app
COPY --from=builder /app/dependencies/ ./
COPY --from=builder /app/spring-boot-loader/ ./
COPY --from=builder /app/snapshot-dependencies/ ./
COPY --from=builder /app/application/ ./
ENV JAVA_OPTS="-XX:+UseG1GC -Xmx1024m -Xms512m -XX:MaxMetaspaceSize=256m -XX:+AlwaysPreTouch"
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/actuator/health || exit 1
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
