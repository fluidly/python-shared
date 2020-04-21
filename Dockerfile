###
# Build dependencies
##
FROM eu.gcr.io/fluidly-registry-15304c60/python:latest-dev AS dependency

COPY Pipfile Pipfile.lock . $APP_DIR/src/
WORKDIR $APP_DIR/src
RUN pipenv install --dev

###
# Build docker image to run tests
##
FROM dependency AS testrunner

COPY --from=dependency --chown=app $APP_DIR $APP_DIR
COPY . $APP_DIR/src
ENV PYTHONPATH=${APP_DIR}/src
