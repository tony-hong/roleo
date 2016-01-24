import errorCode

errorCodeJSON = {
    errorCode.NOUN_FORMAT_ERROR : "exception: noun format error",
    errorCode.VERB_FORMAT_ERROR : "exception: verb format error",
    errorCode.NOUN_EMPTY        : "exception: noun is empty",
    errorCode.VERB_EMPTY        : "exception: verb is empty",
    errorCode.MBR_VEC_EMPTY     : "exception: memberVectors is empty, main query word / semantic role does not exist",
    errorCode.QUERY_EMPTY       : "exception: query is empty, query word does not exist",
    errorCode.SMT_ROLE_EMPTY    : "exception: query.ix[semanticRole] is empty, / semantic role of query word does not exist",
    errorCode.INTERNAL_ERROR    : "exception: internal error",
    errorCode.NON_ENGLISH       : "exception: non english word is temporarily not supported"
}