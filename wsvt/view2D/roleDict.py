'''
    roleDict.py
'''

from models import SemanticRole

def getRoleDict():
    role_list_SDDM = list()
    role_list_TypeDM = list()

    # Get SDDM
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 3
    )
    for r in modelResult:
        role_list_SDDM.append({
            'label'   :   r.labelSDDM,
            'name'    :   r.name
        })
    response = { 'SDDM' : role_list_SDDM }
    
    # Get TypeDM
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 1
    )
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
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 3
    )
    for r in modelResult:
        role_mapping_SDDM[str(r.name)] = [str(r.labelSDDM)]
    
    # Get TypeDM
    modelResult = SemanticRole.objects.exclude(
        modelSupport = 1
    )
    for r in modelResult:
        role_mapping_TypeDM[str(r.name)] = [str(u) for u in r.labelTypeDM.split(',')]

    role_mapping = {
        'SDDM'      :   role_mapping_SDDM,
        'TypeDM'    :   role_mapping_TypeDM
    }
    return role_mapping