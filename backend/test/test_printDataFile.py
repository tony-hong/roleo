import pickle, pprint

file_cake = open('sharevectors/cake-n.pcl', 'rb')
file_animal = open('sharevectors/eat-subject-animal-n.pcl', 'rb')

data1 = pickle.load(file_cake)
print 'file: cake-n.pcl'
pprint.pprint(data1)

data2 = pickle.load(file_animal)
print 'file: eat-subject-animal-n.pcl'
pprint.pprint(data2)