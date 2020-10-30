import os
import unittest
from behave import use_fixture, fixture

import django
from django.test.runner import DiscoverRunner
# Or, if you're feeling lucky, use LiveServerTestCase
from django.test.testcases import TransactionTestCase

os.environ["DJANGO_SETTINGS_MODULE"] = "shit.settings"


@fixture
def django_test_runner(context):
    django.setup()
    context.test_runner = DiscoverRunner()
    context.test_runner.setup_test_environment()
    context.old_db_config = context.test_runner.setup_databases()
    yield
    context.test_runner.teardown_databases(context.old_db_config)
    context.test_runner.teardown_test_environment()


@fixture
def django_test_case(context):
    context.test = TransactionTestCase()
    context.test.setUpClass()
    yield
    context.test.tearDownClass()
    del context.test


def before_all(context):
    use_fixture(django_test_runner, context)


def before_scenario(context, scenario):
    use_fixture(django_test_case, context)
