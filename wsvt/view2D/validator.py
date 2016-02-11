import errorCode
import re


'''
    Validation function for the query for the client

    @return: 
        errorState      = bool
        errorResult    = dict()
'''
def validate(verb, noun, group):
    isValid = False
    errorResult = dict()

    if group == 'noun':
        if noun:
            if not validate_en_String(noun):
                errorResult = {'errCode' : errorCode.NOUN_FORMAT_ERROR}
            else:
                if verb and not validate_en_String(verb):
                    errorResult = {'errCode' : errorCode.VERB_FORMAT_ERROR}
                else:
                    isValid = True
        else:
            # EXCEPTION
            print 'exception: noun is empty'
            errorResult = {'errCode' : errorCode.NOUN_EMPTY}
    elif group == 'verb':
        if verb:
            if not validate_en_String(verb):
                errorResult = {'errCode' : errorCode.VERB_FORMAT_ERROR}
            else:
                if noun and not validate_en_String(noun):
                    errorResult = {'errCode' : errorCode.NOUN_FORMAT_ERROR}
                else:
                    isValid = True
        else:
            # EXCEPTION
            print 'exception: verb is empty'
            errorResult = {'errCode' : errorCode.VERB_EMPTY}
    else:        
        print 'exception: internal error!'
        errorResult = {'errCode' : errorCode.INTERNAL_ERROR}

    # validation passed
    return isValid, errorResult


'''
    Validating function

    @return: bool 
        = True  : 
        = False : format error
'''
def validate_en_String(string):
    result = re.match(r'^[a-z]+$', string)
    return result