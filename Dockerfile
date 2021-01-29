###
# Build dependencies
##
FROM eu.gcr.io/fluidly-registry-15304c60/python:latest-dev AS dependency

# Add ssh key
ARG SSH_PRIVATE_KEY
RUN mkdir $APP_DIR/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" > $APP_DIR/.ssh/id_rsa
RUN chmod 600 $APP_DIR/.ssh/id_rsa

# Make sure your domain is accepted
RUN touch $APP_DIR/.ssh/known_hosts
RUN echo 'github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==' \
    >> $APP_DIR/.ssh/known_hosts

COPY --chown=app Pipfile Pipfile.lock . $APP_DIR/src/
WORKDIR $APP_DIR/src
RUN pipenv install --dev

###
# Build docker image to run tests
##
FROM dependency AS testrunner

COPY --from=dependency --chown=app $APP_DIR $APP_DIR
COPY . $APP_DIR/src
ENV PYTHONPATH=${APP_DIR}/src
