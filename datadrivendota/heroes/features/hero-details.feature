Feature: Hero details
    In order to see their basic stats
    As a competitor
    I want to see hero details

    Scenario:
        Given the user is "kit"
          And the user accesses the url "/heroes/"
         When the user clicks on "Death Prophet"
         Then the page contains the h1 "Death Prophet"
          And the page contains the skill charts
