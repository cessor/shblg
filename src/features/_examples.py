"""
This is an older feature file I carried over from a previous project
to bootstrap behave testing for this blog.

Feature: Person visits the website for the first time
    Scenario: Browsing for books
        Given I am not registered
        And I visit the library
        Then I can browse all books
        But I can't add new ones

    Scenario: Adding a book to the library
        Given I am registered
        And I visit the library
        When I add a book
            | Title                                           | Author        |
            | Patterns of Enterprise Application Architecture | Martin Fowler |
        Then I am the book's caretaker
        And the book was added today
        And I own a copy of the book
        And I can see the following data about it
            | Label      | Value                                           |
            | Title      | Patterns of Enterprise Application Architecture |
            | Author     | Martin Fowler                                   |
"""

# pylint: skip-file
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nose.tools import *

@given(u'I visit the library')
def setup_visit_the_library(context):
    URL = 'http://localhost:8000/'
    context.browser.get(URL)
    assert_true('Library' in context.browser.title)
    assert_true('Books' in context.browser.title)


@given(u'I am not registered')
def step_not_logged_in(context):
    context.browser.get('http://localhost:8000/admin/logout/')


@given(u'I am registered')
def setup_login(context):
    context.browser.get('http://localhost:8000/admin/login/?next=/')

    login_form = context.browser.find_element_by_id('login-form')

    username = context.browser.find_element_by_id('id_username')
    username.send_keys(context.user.username)

    id_password = context.browser.find_element_by_id('id_password')
    id_password.send_keys(context.user.password)

    login_form.submit()

    wait = WebDriverWait(context.browser, 3)
    welcome_banner = wait.until(
        #EC.presence_of_element_located((By.ID, 'Libr'))
        EC.title_is('Library | Books')
    )


@then(u'I can browse all books')
def verify_see_all_books(context):
    books = context.browser.find_element_by_id('books_table')
    assert_true(books)


@then(u'I can\'t add new ones')
def verify_cant_add_new_ones(context):
    assert_raises(
        Exception,
        lambda: context.browser.find_element_by_id('new_book_form')
    )


@when(u'I add a book')
def exercise_add_a_book(context):

    form = context.browser.find_element_by_id('new_book_form')

    assert_true(form)
    book, *_ = context.table

    title = context.browser.find_element_by_id('id_title')
    title.send_keys(book.get('Title'))

    author = context.browser.find_element_by_id('id_author')
    author.send_keys(book.get('Author'))

    form.submit()

    wait = WebDriverWait(context.browser, 3)
    book_title = wait.until(
        EC.presence_of_element_located((By.ID, 'book_title'))
    )


@then(u'I am the book\'s caretaker')
def verify_caretaker(context):
    label_caretaker = context.browser.find_element_by_class_name('label_caretaker')
    assert_true(context.user.username in label_caretaker.text)


@then(u'I own a copy of the book')
def verify_copy(context):
    book_owner = context.browser.find_element_by_class_name('book_owner')
    assert_true(context.user.name in book_owner.text)


@then(u'I can see the following data about it')
def verify_info(context):
    for row in context.table:
        name = row['Label'].lower()
        value = row['Value'].lower()
        label = context.browser.find_element_by_class_name('label_' + name)
        assert_true(value in label.text)


@then(u'the book was added today')
def verify_date(context):
    date_added = context.browser.find_element_by_class_name('label_date_added')
    MONTH_DD_YYYY = '%b %d, %Y'
    import datetime
    today = datetime.datetime.strftime(datetime.date.today(), MONTH_DD_YYYY)
    assert_true(today in date_added.text)


@given(u'the django server is running')
def step_impl(context):
    #from subprocess import call
    #call(["python", "manage.py", "runserver"])
    pass


@given(u'I opened the login page')
def step_impl(context):
    context.browser.get('http://localhost:8000/admin/')


@given(u'I see the login form')
def step_impl(context):
    login_form = context.browser.find_element_by_id('login-form')
    username = context.browser.find_element_by_id("id_username")
    password = context.browser.find_element_by_id("id_password")
    assert_true(login_form)
    assert_true(username)
    assert_true(password)


@when(u'I enter my username')
def step_impl(context):
    username = context.browser.find_element_by_id("id_username")
    username.send_keys("testuser")


@when(u'I enter my password')
def step_impl(context):
    password = context.browser.find_element_by_id("id_password")
    password.send_keys("sXR$)NuVi6cG9h6LFgp[$PEL")


@when(u'I submit the form')
def step_impl(context):
    context.browser.find_element_by_tag_name("form").submit()


@then(u'I should be logged in')
def step_impl(context):
    wait = WebDriverWait(context.browser, 3)
    welcome_banner = wait.until(
        EC.presence_of_element_located((By.ID, 'user-tools'))
    )
    assert_true(welcome_banner)


@then(u'see the admin view')
def step_impl(context):
    assert_true('Website-Verwaltung' in context.browser.title)
