'''
    This module contains the mapping from error code to the message which will 
    be shown on the web page

    @Author: 
        Tony Hong
'''

import errorCode

errorCodeJSON = {
    errorCode.NOUN_FORMAT_ERROR : "Noun format error",
    errorCode.VERB_FORMAT_ERROR : "Verb format error",
    errorCode.NOUN_EMPTY        : "This noun as a selector does not exist in this model.",
    errorCode.VERB_EMPTY        : "This verb as a selector does not exist in this model.",
    errorCode.MBR_VEC_EMPTY     : "The model return nothing for this selector with this role. Enter another query.", # MemberVectors is empty, main query word 
    errorCode.QUERY_EMPTY       : "The query word does not exist in this model",      # query is empty
    errorCode.SMT_ROLE_EMPTY    : "Semantic role of the query word does not exist in this model",  # query.ix[semanticRole] is empty
    errorCode.INTERNAL_ERROR    : "Server internal error. Please refresh the page",
    errorCode.NOT_IN_EMBEDDING  : "Returned word in the distributional model is not in the word embedding. Try a smaller top N",
    errorCode.NON_ENGLISH       : "Non english word is temporarily not supported",
    errorCode.TON_N_ERROR       : "Top N is out of range",
}