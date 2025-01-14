import app
import pytest
import os
from myutils import myutils

@pytest.fixture(scope='module')
def test_client():
    os.environ['APP_ENV']='Test'
    flask_app = app.create_app()
    app.hostname=""
    app.username=""
    app.nodename=""
    app.password=""
    app.adusername=""
    app.adpassword=""
    app.port=""
    app.auth=""
    app.adauth=""    

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
    app.port=app.default_port
    app.protocol=app.default_protocol
    app.https_mapping=app.default_https_mapping
    app.ehr_base_version=app.default_ehrbase_version
    app.username=app.default_username
    app.nodename=app.default_nodename
    app.password=app.default_password
    app.adusername=app.default_adusername
    app.adpassword=app.default_adpassword
    app.url_base,app.url_base_ecis,app.url_base_admin,app.url_base_management=myutils.setEHRbasepaths(app.hostname,app.port,app.protocol,app.https_mapping)
    app.auth="fakeauth"
    app.adauth="fakeauth"
    # app.url_base=
    # app.url_base_ecis=

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!

@pytest.fixture(scope='module')
def test_client_with_real_info():
    os.environ['APP_ENV']='Test'
    flask_app = app.create_app()
    print(f'testing url_base={flask_app.url_base} auth={flask_app.auth}')

    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!

   