# bin/robot-server collective.futures.testing.FUTURES_ROBOT_TESTING
# bin/robot src/collective/futures/tests/test_acceptance.robot

*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Start futures logging  Open test browser
Test Teardown  Run keywords   Stop futures logging  Close all browsers

*** Test Cases ***

Result
    Go to  ${PLONE_URL}/testing-result
    Element should contain  test-content   testing-result
    Log should contain  echo: testing-result
    Log should contain  all: futures.testing
    Log should not contain  multiprocess: futures.testing

Result or submit
    Go to  ${PLONE_URL}/testing-result-or-submit
    Element should contain  test-content   testing-result-or-submit
    Log should contain  echo: testing-result-or-submit
    Log should contain  all: futures.testing
    Log should not contain  multiprocess: futures.testing

Result or submit placeholder
    Go to  ${PLONE_URL}/testing-result-or-submit-placeholder
    Element should contain  test-content   placeholder
    Log should not contain  echo: testing-result-or-submit
    Log should not contain  all: futures.testing

Result multiprocess
    Go to  ${PLONE_URL}/testing-result-multiprocess
    Element should contain  test-content   testing-result-multiprocess
    Log should contain  multiprocess: futures.testing
    Log should contain  all: futures.testing
    Log should not contain  echo: testing-result-multiprocess
    # ^ because the log is lost in separate process

Result or submit multiprocess
    Go to  ${PLONE_URL}/testing-result-or-submit-multiprocess
    Element should contain  test-content   testing-result-or-submit-multiprocess
    Log should contain  multiprocess: futures.testing
    Log should contain  all: futures.testing
    Log should not contain  echo: testing-result-or-submit-multiprocess
    # ^ because the log is lost in separate process

Transaction abort
    Go to  ${PLONE_URL}/testing-transaction-abort
    Element should contain  test-content   transaction-abort
    Log should contain  echo: testing-result
    Log should contain  all: futures.testing
    Log should not contain  multiprocess: futures.testing

Transaction commit
    Go to  ${PLONE_URL}/testing-transaction-commit
    Element should contain  test-content   transaction-commit
    Log should contain  echo: testing-result
    Log should contain  all: futures.testing
    Log should not contain  multiprocess: futures.testing


*** Keywords ***

Log should contain
  [Arguments]  ${needle}
  ${haystack} =  Get futures log
  Should contain  ${haystack}  ${needle}

Log should not contain
  [Arguments]  ${needle}
  ${haystack} =  Get futures log
  Should not contain  ${haystack}  ${needle}
