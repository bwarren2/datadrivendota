Feature: Hero details
    In order to see their basic stats
    As a competitor
    I want to see hero details

    Scenario:
        Given I am logged in as "kit"
          And I go to "/heroes/"
         When I click on "Death Prophet"
         Then I will see "Death Prophet"
          And I will see the skill charts
