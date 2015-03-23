expected_type ='''
You are using the wrong type of Alveare exception.
Expected input type: {}'''

unmarshalling_error ='''
Missing field: "{}" while deserializing:
{}'''

marshalling_error ='''
Missing field: "{}" while serializing:
{}'''

validation_error ='''
Validation error:
{}
while validating:
{}
'''

forced_error ='''
Forced error:
{}
while validating:
{}
'''

HTTP_STATUS_CODES = {
    400:    'Bad Request',
    404:    'Resource Not Found',
    500:    'Internal Server Error',
}
