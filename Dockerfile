###
# Build dependencies
##
FROM eu.gcr.io/fluidly-registry-15304c60/python:latest-dev AS dependency

COPY Pipfile Pipfile.lock $APP_DIR/src/
WORKDIR $APP_DIR/src
RUN pipenv install --deploy

###
# Build docker image to run tests
##
FROM dependency AS testrunner

COPY --from=dependency --chown=app $APP_DIR $APP_DIR
COPY . $APP_DIR/src
ENV PYTHONPATH=${APP_DIR}/src

###
# Build runtime Docker image
##
FROM eu.gcr.io/fluidly-registry-15304c60/python:latest AS runtime

COPY --from=dependency $APP_DIR $APP_DIR
COPY . $APP_DIR/src


ENV PYTHONPATH=${APP_DIR}/src
WORKDIR $APP_DIR/src

