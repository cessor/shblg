Feature: Authoring drafts
    Articles without 'published' date are drafts.
    They can be edited by authors, given the right permissions.

    Background: Authorship
        Given I am an author
        And I have logged in
        And I have permissions to view and publish drafts

    Scenario: Authoring a draft
        When I am writing an article
        And I set the published date to None
        Then I the article becomes a draft

    Scenario: Drafts page appears in main menu
        Given I have written a draft
        When I am on the index page
        Then I can see a menu item that leads me to the drafts page
        But I don't see the draft

    Scenario: Anonymous drafts make main menu item appear
        Given an anonymous draft
        When I am on the index page
        Then I can see a menu item that leads me to the drafts page

    Scenario: My drafts
        Given I have written a draft
        When I am on the drafts page
        Then I can see the draft

    Scenario: Other's drafts
        Given somebody else has written a draft
        When I am on the drafts page
        Then I can't see that draft

    Scenario: Anonymous drafts
        Given an article without an author
        When I am on the drafts page
        Then I can see the anonymous draft

    Scenario: Inspecting a draft
        Given I have written a draft
        When I am on the drafts page
        Then I can see its content

    Scenario: Note on draft
        Given I have written a draft
        When I am inspecting the draft
        Then I am notified that it has not yet been published

    Scenario: Note to publish now
        Given I have written a draft
        When I am inspecting the draft
        Then I am offered to publish it right away

    Scenario: Publish now
        Given I have written a draft
        When I publish it
        Then I am redirected to the published article

    Scenario: Publish now (Denied)
        Given I have written a draft
        And I don't have the permissions to publish a draft
        When I try to publish it
        Then the article is not published

    Scenario: Visitors don't see drafts item in main menu
        Given I am not logged in
        When I am on the index page
        Then I don't see a menu item for drafts

    Scenario: Visitors can't inspect drafts
        Given I am not logged in
        When I try accessing the drafts page
        Then I am asked to login
        When I try inspecting a specific draft
        Then I am asked to login

    Scenario: Drafts don't count into tags
        Given I have written a draft
        And the draft is tagged
        When I am on the tags page
        Then the article does not activate the tag

    Scenario: Drafts don't show on author pages
        Given I have written a draft
        When I am on my author page
        Then the draft does not appear in my list of articles