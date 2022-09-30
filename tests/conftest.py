import app
import pytest
import os

@pytest.fixture(scope='module')
def test_client():
    os.environ['APP_ENV']='Test'
    flask_app = app.create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
def test_client_with_globalvars():
    os.environ['APP_ENV']='Test'
    flask_app = app.create_app()
    app.hostname=app.default_hostname
    app.username=app.default_username
    app.nodename=app.default_nodename
    app.password=app.default_password
    app.port=app.default_port
    app.auth=""

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!

   