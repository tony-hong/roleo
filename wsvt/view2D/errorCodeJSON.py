import errorCode

errorCodeJSON = {
    errorCode.NOUN_FORMAT_ERROR : "Noun format error",
    errorCode.VERB_FORMAT_ERROR : "Verb format error",
    errorCode.NOUN_EMPTY        : "Noun as primal query word is empty",
    errorCode.VERB_EMPTY        : "Verb as primal query word is empty",
    errorCode.MBR_VEC_EMPTY     : "The model return nothing for the primal query word", # MemberVectors is empty, main query word / 
    errorCode.QUERY_EMPTY       : "Second query word does not exist in the model",      # query is empty, 
    errorCode.SMT_ROLE_EMPTY    : "Semantic role of second query word does not exist",  # query.ix[semanticRole] is empty, / 
    errorCode.INTERNAL_ERROR    : "Server internal error, please refresh the page",
    errorCode.NON_ENGLISH       : "Non english word is temporarily not supported",
    errorCode.TON_N_ERROR       : "TopN is out of range"

}