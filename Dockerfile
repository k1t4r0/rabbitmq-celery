FROM rabbitmq:3-management

# Copy definitions file
COPY init/definitions.json /etc/rabbitmq/definitions.json

# Set proper permissions
RUN chown rabbitmq:rabbitmq /etc/rabbitmq/definitions.json && \
    chmod 644 /etc/rabbitmq/definitions.json && \
    # Verify file exists and is readable
    ls -l /etc/rabbitmq/definitions.json

# Create and set permissions for custom config
RUN echo '[{rabbit, [{load_definitions, "/etc/rabbitmq/definitions.json"}]}].' > /etc/rabbitmq/advanced.config && \
    chown rabbitmq:rabbitmq /etc/rabbitmq/advanced.config && \
    chmod 644 /etc/rabbitmq/advanced.config

# Enable management plugin
RUN rabbitmq-plugins enable rabbitmq_management

# Environment variables
ENV RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS="-rabbitmq_management load_definitions \"/etc/rabbitmq/definitions.json\""
ENV RABBITMQ_LOAD_DEFINITIONS=/etc/rabbitmq/definitions.json