import os
import unittest
from behave import use_fixture, fixture

import django
from django.test.runner import DiscoverRunner
# Or, if you're feeling lucky, use LiveServerTestCase
from django.test.testcases import TransactionTestCase
from django.test import TestCase

os.environ["DJANGO_SETTINGS_MODULE"] = "shit.settings"


def before_all(context):
    django.setup()
    context.test_runner = DiscoverRunner()
    context.test_runner.setup_test_environment()
    context.old_db_config = context.test_runner.setup_databases()


def after_all(context):
    context.test_runner.teardown_databases(context.old_db_config)
    context.test_runner.teardown_test_environment()


def before_scenario(context, scenario):
    context.test = TestCase()
    context.test.setUpClass()


def after_scenario(context, scenario):
    context.test.tearDownClass()
    del context.test
