
from SaxElementState import SAXElementState
from BaseSAXHandler import BaseSAXHandler


class ModelContentHandler(BaseSAXHandler):

    def __init__(self, types_dict):
    	super(ModelContentHandler, self).__init__()
        self.types_dict = types_dict
        # delayAttributeStates gets iterated over when done parsing.
        # All the attributes are set as a last step to ensure,
        # references to instances can be resolved (see endDocument)
        self.delayedPropertySettings = []
        self.delayedCollectionAdditions = []
        self.rootObject = None

    def startElementNS(self, name, qname, attrs):
        """Parses an XML element"""
    	thisState, parent_state = super(ModelContentHandler, self).startElementNS(name, qname, attrs)

        # cannot handle unicode named attributes, convert everything to ascii
        plain_name = name[1].encode('ascii', errors='ignore')

        # The uppercase convention is in the C# code, too.
        # (not used necessarily, only used to find out what kind of element we're dealing with here)
        plain_name = plain_name.upper()
        print("startElementNS for: " + str(name))

        # get the type arguments for plain_name
        # (in case of a collection/generic this will be the type it contains e.g. List<TypeArgument>)
        # this will also be created for the root element but discarded since the root does not have a parent,
        # so ignore in case of root
        fullAttrTypeName = "typeArgsOf" + plain_name  # typeArgsOfSOMETHING gets automatically generated into the result

        if hasattr(parent_state.elementBinding, fullAttrTypeName): #check if parent knows what type the element should be
            ele_bind = getattr(parent_state.elementBinding, fullAttrTypeName)
            if (len(ele_bind) != 1):
                raise Exception("Type " + plain_name + " has more than one type argument. Unkown collection type.")
            thisState.elementBinding = ele_bind[0]

            # since it's a child it has to be contained in a collection,
            # resolve the collection the bindin_instance will be put in
            # maybe change after model repositories are implemented
            thisState.addCollectionAdditionDelay(
                thisState.parentState.bindingInstance.GetCollectionForFeature(plain_name))

        elif (plain_name in self.types_dict): #is root element
            print(plain_name + " is the root element")
            thisState.elementBinding = self.types_dict[plain_name]
        else:
            raise Exception("FATAL ERROR: Unkown type " + name[1] + "!")

        binding_object = thisState.startBindingElement(thisState.elementBinding, attrs)

        if (self.rootObject is None):
            self.rootObject = binding_object

            #replace dummy parent state of root with itself
            #TODO: AFTER MODEL REPOSITORY RESOLVE WAS IMPLEMENTED
            #REMOVE THIS/ THIS IS ONLY A TEMPORARY WORKAROUND
            thisState.parentState = thisState



    def endElementNS(self, name, qname):
    	thisState = super(ModelContentHandler, self).endElementNS(name, qname)
    	bindingObject, newCollectionAdditions, newPropertySettings = thisState.endBindingElement()
        self.delayedCollectionAdditions += newCollectionAdditions
        self.delayedPropertySettings += newPropertySettings

    def endDocument(self):
        for d in self.delayedCollectionAdditions:
            d.execute()

        for d in self.delayedPropertySettings:
            d.execute()
