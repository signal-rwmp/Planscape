####################################################################################
# Builder; this creates Python Wheels, which makes the deployed image smaller

FROM python:3.10.9 as builder

# set work directory
WORKDIR /src/planscape

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install binary dependencies
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev r-base-core

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


####################################################################################
# Deployed image

FROM python:3.10.9

# create the appropriate directories
ENV APP_HOME=/home/planscape/backend
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y gdal-bin
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /src/planscape/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

CMD ["uwsgi", "--ini", "./planscape/uwsgi.ini"]
