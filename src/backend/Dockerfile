FROM dataformer/backend_build as backend_build

FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install git -y

COPY --from=backend_build /app/dist/*.whl /app/
RUN pip install dfapp-*.whl
RUN rm *.whl

EXPOSE 80

CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "7860", "--factory", "dfapp.main:create_app" ]
