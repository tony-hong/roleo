import re
import logging

import view2D.errorCode as errorCode

logger = logging.getLogger('django')

'''
    Validation function for the query for the client

    @return: 
        isValid      = bool()
        errorResult  = dict()
'''
def validate(verb, noun, group, topN):
    isValid = False
    errorResult = dict()

    if topN > 100 or topN < 5:
        logger.critical( 'errCode: %d. topN is out of range', errorCode.TON_N_ERROR)
        errorResult = {'errCode' : errorCode.TON_N_ERROR}
        return isValid, errorResult

    if group == 'noun':
        if noun:
            if not validate_en_String(noun):
                logger.error( 'errCode: %d. noun format error', errorCode.NOUN_FORMAT_ERROR)
                errorResult = {'errCode' : errorCode.NOUN_FORMAT_ERROR}
            else:
                if verb and not validate_en_String(verb):
                    logger.error( 'errCode: %d. verb format error', errorCode.VERB_FORMAT_ERROR)
                    errorResult = {'errCode' : errorCode.VERB_FORMAT_ERROR}
                else:
                    isValid = True
        else:
            # EXCEPTION
            logger.error( 'errCode: %d. noun is empty', errorCode.NOUN_EMPTY)
            errorResult = {'errCode' : errorCode.NOUN_EMPTY}
    elif group == 'verb':
        if verb:
            if not validate_en_String(verb):
                logger.error( 'errCode: %d. verb format error', errorCode.VERB_FORMAT_ERROR)
                errorResult = {'errCode' : errorCode.VERB_FORMAT_ERROR}
            else:
                if noun and not validate_en_String(noun):
                    logger.error( 'errCode: %d. noun format error', errorCode.NOUN_FORMAT_ERROR)
                    errorResult = {'errCode' : errorCode.NOUN_FORMAT_ERROR}
                else:
                    isValid = True
        else:
            # EXCEPTION
            logger.error( 'errCode: %d. verb is empty', errorCode.VERB_EMPTY)
            errorResult = {'errCode' : errorCode.VERB_EMPTY}
    else:
        logger.critical( 'errCode: %d. internal error!', errorCode.INTERNAL_ERROR)
        errorResult = {'errCode' : errorCode.INTERNAL_ERROR}

    # validation passed
    return isValid, errorResult


'''
    Validating function
    Check if the string is 

    @return: bool 
        = True  : 
        = False : format error
'''
def validate_en_String(string):
    result = re.match(r'^[a-z]+$', string)
    return result