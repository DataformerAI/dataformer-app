# celeryconfig.py
import os

dfapp_redis_host = os.environ.get("DFAPP_REDIS_HOST")
dfapp_redis_port = os.environ.get("DFAPP_REDIS_PORT")
# broker default user

if dfapp_redis_host and dfapp_redis_port:
    broker_url = f"redis://{dfapp_redis_host}:{dfapp_redis_port}/0"
    result_backend = f"redis://{dfapp_redis_host}:{dfapp_redis_port}/0"
else:
    # RabbitMQ
    mq_user = os.environ.get("RABBITMQ_DEFAULT_USER", "dfapp")
    mq_password = os.environ.get("RABBITMQ_DEFAULT_PASS", "dfapp")
    broker_url = os.environ.get("BROKER_URL", f"amqp://{mq_user}:{mq_password}@localhost:5672//")
    result_backend = os.environ.get("RESULT_BACKEND", "redis://localhost:6379/0")
# tasks should be json or pickle
accept_content = ["json", "pickle"]
