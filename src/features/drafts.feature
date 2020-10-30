Feature: Drafts
    Articles without 'published' date are drafts.

    Background: Authorship
        Given I am an author
        And I have logged in

    Scenario: Authoring a draft
        When I am writing an article
        And I set the published date to None
        Then I the article becomes a draft

    Scenario: Drafts page appears in main menu
        Given I have written a draft
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

    Scenario: Inspecting a draft
        Given I have written a draft
        When I am on the drafts page
        Then I can inspect the draft

    Scenario: Note on draft
        Given I have written a draft
        When I am inspecting the draft
        Then I am notified that it has not yet been published

    Scenario: Publish now
        Given I view a draft
        Then I am offered to publish it right away

    Scenario: Visitors don't see drafts item in main menu
        Given I am not logged in
        Then I don't see a menu item for drafts

    Scenario: Visitors can't inspect drafts
        Given I am not logged in
        When I try accessing the drafts page
        Then I am asked to login
        When I try inspecting a specific draft
        Then I am asked to login
