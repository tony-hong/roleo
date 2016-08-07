'''
    roleDict.py
'''

from models import SemanticRole

def getRoleDict():
    role_list_SDDM = list()
    role_list_TypeDM = list()
    role_list_SDDM_Embedding = list()

    # Get SDDM
    modelResult = SemanticRole.objects.all()
    for r in modelResult:
        role_list_SDDM.append({
            'label'   :   r.labelSDDM,
            'name'    :   r.name
        })
    response = { 
        'SDDM'              : role_list_SDDM,
    }

    # Get RBE
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 0
    ).exclude(
        modelSupport = 1
    )
    
    for r in modelResult:
        role_list_SDDM_Embedding.append({
            'label'   :   r.labelSDDM,
            'name'    :   r.name
        })
    response['RBE'] = role_list_SDDM_Embedding
    response['W2V'] = role_list_SDDM_Embedding
    
    # Get TypeDM
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 1
    ).exclude(
        modelSupport = 2
    )

    print modelResult

    for r in modelResult:
        role_list_TypeDM.append({
            'label'   :   r.labelTypeDM,
            'name'    :   r.name
        })
    response['TypeDM'] = role_list_TypeDM

    return response


def getRoleMapping():
    role_mapping = dict()

    role_mapping_SDDM = dict()    
    role_mapping_TypeDM = dict()

    # Get SDDM
    modelResult = SemanticRole.objects.all()
    for r in modelResult:
        role_mapping_SDDM[str(r.name)] = [str(r.labelSDDM)]
    
    # Get TypeDM
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 1
    ).exclude(
        modelSupport = 2
    )

    for r in modelResult: 
        role_mapping_TypeDM[str(r.name)] = [str(u) for u in r.labelTypeDM.split(',')]

    role_mapping = {
        'SDDM'              :   role_mapping_SDDM,
        'TypeDM'            :   role_mapping_TypeDM,
        'RBE'               :   role_mapping_SDDM,
        'W2V'               :   role_mapping_SDDM,
    }
    return role_mapping