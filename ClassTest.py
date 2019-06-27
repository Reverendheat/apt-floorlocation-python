#from classfilename import theclass
from SQLServerClasses import SQLServerFunctions

ermf = SQLServerFunctions() #making an instance of the class
garbage = '(asdff'
withoutGarbage = ermf.RemoveTupleGarbage(garbage)

print(withoutGarbage)
partNumber = '30060'
isValid = ermf.PartExistsTest(partNumber)
print(isValid)