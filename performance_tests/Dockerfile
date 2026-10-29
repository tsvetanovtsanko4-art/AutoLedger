# JMeter image for distributed runs, pinned to the same version as local runs.
FROM eclipse-temurin:21-jre
ARG JMETER_VERSION=5.6.3
RUN curl -fsSL "https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz" \
    | tar -xz -C /opt \
    && ln -s "/opt/apache-jmeter-${JMETER_VERSION}/bin/jmeter" /usr/local/bin/jmeter \
    && ln -s "/opt/apache-jmeter-${JMETER_VERSION}/bin/jmeter-server" /usr/local/bin/jmeter-server
WORKDIR /tests
