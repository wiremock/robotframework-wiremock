*** Settings ***
Library  String
Library  Collections
Library  RequestsLibrary
Library  WireMockLibrary
Suite Setup  Create Sessions
Test Teardown  Reset Wiremock


*** Variables ***
${WIREMOCK_URL}
${ENDPOINT}  /endpoint
&{BODY}  var1=value1  var2=value2
&{HEADERS}  Content-Type=application/json  Cache-Control=max-age\=3600
${MOCK_REQ}  {"method": "GET", "url": "${ENDPOINT}"}
${MOCK_RSP}  {"status": 200}
${MOCK_DATA}  {"request": ${MOCK_REQ}, "response": ${MOCK_RSP}}


*** Test Cases ***
Success On Expected GET
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Success  ${ENDPOINT}

Failure On GET With Mismatched Method
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send POST Expect Failure  ${ENDPOINT}

Failure On GET With Mismatched Endpoint
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Failure  /mismatched

Success On Expected GET With Path Pattern
    &{req}=  Create Mock Request Matcher  GET  /endpoint.*  url_match_type=urlPathPattern
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Success  /endpoint-extended/api

Success On Expected GET With Header Matching
    &{match_headers}=  Create Dictionary  header1=value1  header2=value2
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}  headers=${match_headers}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Success  ${ENDPOINT}  request_headers=${match_headers}

Failure On GET With Mismatched Header
    &{match_headers}=  Create Dictionary  header1=value1  header2=value2
    &{mismatched_headers}=  Create Dictionary  header1=mismatch  header2=value2
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}  headers=${match_headers}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Failure  ${ENDPOINT}  request_headers=${mismatched_headers}

Success On Expected GET With Specified Data
    Create Mock Mapping With Data  ${MOCK_DATA}
    Send GET Expect Success  ${ENDPOINT}

Success On Expected GET With Status Message
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}
    &{rsp}=  Create Mock Response  status=200  status_message=Ok
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Success  ${ENDPOINT}  response_status_message=Ok

Success On Expected GET With Response Body
    &{req}=  Create Mock Request Matcher  GET  ${ENDPOINT}
    &{rsp}=  Create Mock Response  status=200  headers=${HEADERS}  json_body=${BODY}
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Success  ${ENDPOINT}  response_headers=${HEADERS}  response_body=${BODY}

Success On Expected POST With Body
    &{req}=  Create Mock Request Matcher  POST  ${ENDPOINT}  json_body=${BODY}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    Send POST Expect Success  ${ENDPOINT}  ${BODY}

Failure On POST With Mismatched Body
    &{req}=  Create Mock Request Matcher  POST  ${ENDPOINT}  json_body=${BODY}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    &{mismatched}=  Create Dictionary  var1=mismatch  var2=value2
    Send POST Expect Failure  ${ENDPOINT}  ${mismatched}

Failure On POST With Partial Body
    &{req}=  Create Mock Request Matcher  POST  ${ENDPOINT}  json_body=${BODY}
    &{rsp}=  Create Mock Response  status=200
    Create Mock Mapping  ${req}  ${rsp}
    &{partial}=  Create Dictionary  var1=value1
    Send POST Expect Failure  ${ENDPOINT}  ${partial}

Success On Default GET Mapping
    Create Default Mock Mapping  GET  ${ENDPOINT}
    Send GET Expect Success  ${ENDPOINT}

Success On Default GET Mapping With Response Body
    Create Default Mock Mapping  GET  ${ENDPOINT}  response_headers=${HEADERS}  response_body=${BODY}
    Send GET Expect Success  ${ENDPOINT}  response_headers=${HEADERS}  response_body=${BODY}

Success On Templated Response
    &{template_body}=  Create Dictionary  path_var={{request.path.[0]}}
    &{response_body}=  Create Dictionary  path_var=templated
    &{req}=  Create Mock Request Matcher  GET  /templated
    &{rsp}=  Create Mock Response  status=200  json_body=${template_body}  template=${True}
    Create Mock Mapping  ${req}  ${rsp}
    Send GET Expect Success  /templated  response_body=${response_body}

*** Keywords ***
Create Sessions
    Create Session  server  ${WIREMOCK_URL}
    Create Mock Session  ${WIREMOCK_URL}

Reset Wiremock
    Reset Mock Mappings

Send GET Expect Success
    [Arguments]  ${endpoint}=${ENDPOINT}
    ...          ${request_headers}=${None}
    ...          ${response_status_message}=${None}
    ...          ${response_headers}=${None}
    ...          ${response_body}=${None}
    ${rsp}=  Get Request  server  ${endpoint}  ${request_headers}
    Log  ${rsp.text}
    Should Be Equal As Strings  ${rsp.status_code}  200
    Run Keyword If   ${response_status_message != None}
    ...              Should Be Equal As Strings  ${response_status_message}  ${rsp.reason}
    Run Keyword If   ${response_headers != None}
    ...              Verify Response Headers  ${response_headers}  ${rsp.headers}
    Run Keyword If   ${response_body != None}
    ...              Verify Response Body  ${response_body}  ${rsp.json()}

Send GET Expect Failure
    [Arguments]  ${endpoint}=${ENDPOINT}  ${request_headers}=${None}  ${response_code}=404
    ${rsp}=  Get Request  server  ${endpoint}  ${request_headers}
    Should Be Equal As Strings  ${rsp.status_code}  ${response_code}

Send POST Expect Success
    [Arguments]  ${endpoint}=${ENDPOINT}  ${body}=${BODY}  ${response_code}=200
    Send POST  ${endpoint}  ${body}  ${response_code}

Send POST Expect Failure
    [Arguments]  ${endpoint}=${ENDPOINT}  ${body}=${BODY}  ${response_code}=404
    Send POST  ${endpoint}  ${body}  ${response_code}

Send POST
    [Arguments]  ${endpoint}  ${body}  ${response_code}
    ${body_json}=  Evaluate  json.dumps(${body})  json
    ${rsp}=  Post Request  server  ${endpoint}  data=${body_json}
    Should Be Equal As Strings  ${rsp.status_code}  ${response_code}

Verify Response Headers
    [Arguments]  ${expected}  ${actual}
    Dictionary Should Contain Sub Dictionary  ${actual}  ${expected}

Verify Response Body
    [Arguments]  ${expected}  ${actual}
    Dictionaries Should Be Equal  ${expected}  ${actual}
