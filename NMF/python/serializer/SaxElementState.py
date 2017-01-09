from pdb import set_trace as bp
# def bp():
#     pass

class SAXElementState (object):
    """State required to generate bindings for a specific element."""

    # The binding instance being created for this element.
    __bindingInstance = None

    # The schema binding for the element being constructed.
    __elementBinding = None

    def setElementBinding(self, element_binding):
        """Record the binding to be used for this element.

        Generally ignored, except at the top level this is the only way to
        associate a binding instance created from an xsi:type description with
        a specific element."""
        self.__elementBinding = element_binding

    def setTargetContainer(self, target_container):
        self.targetContainer = target_container


    def getTargetContainer(self):
        return self.targetContainer

    def getElementBinding(self):
        return self.__elementBinding

    def getBindingInstance(self):
        return self.__bindingInstance

    def __init__(self, **kw):
        super(SAXElementState, self).__init__()
        self.__bindingInstance = None
        self.__parentState = kw.get('parent_state')
        self.__contentHandler = kw.get('content_handler')
        self.targetContainer = None
        self.__content = []
        parent_state = self.parentState()

    # Create the binding instance for this element.
    def __constructElement(self, type_class, attrs, constructor_parameters=None):

        if constructor_parameters is None:
            constructor_parameters = []
        self.__bindingInstance = type_class(*constructor_parameters)


        self.attrs = attrs


        return self.__bindingInstance

    def startBindingElement(self, type_class, attrs):
        """Actions upon entering an element that will produce a binding instance.

        Wrapper for constructElement

        @param type_class: The Python type (class) of the binding instance
        @param attrs: The XML attributes associated with the element
        @type attrs: C{xml.sax.xmlreader.Attributes}
        @return: The generated binding instance
        """
        self.__constructElement(type_class, attrs)
        return self.__bindingInstance

    def endBindingElement(self):
        """Perform any end-of-element processing."""

        # at this point only the element instance exists, it is not populated yet

        # add to parent
        #if it's None it's the root element which is not contained anywhere
        tc = self.targetContainer
        if self.targetContainer != None:
            self.targetContainer.Add(self.__bindingInstance)
        # else:
        #     print(str(self.__bindingInstance) + " DOES NOT HAVE A CONTAINER. IS ROOT ELEMENT?")
        return self.__bindingInstance

    #handles the parsing and resolving attributes for an element
    def parseAttributes(self):
        # Set instance attributes
        #bp()
        for attr_name in self.attrs.getNames():

            # Ignore xmlns and xsi attributes
            if (attr_name[0] is not None and attr_name[0] in ("http://www.omg.org/XMI")):
                continue

            # attributes
            plain_name = attr_name[1].encode('ascii', errors='ignore')
            plain_name = plain_name.upper()
            value = self.attrs.getValue(attr_name)

            if (value[:2] == '//'):
                if(value[2] == '@'):
                    #TODO: not only support parent container references... REDO when Model Repositroy is implemented
                    value = (value[3:]).encode('ascii', errors='ignore')
                    attr_container, index = value.split('.')
                    index = int(index)
                    attr_container = attr_container.upper()

                    try:
                        value = self.parentState().getBindingInstance().GetModelElementForReference(attr_container, index)
                    except Exception, e:
                        from pdb import set_trace
                        set_trace()
                        raise e
                else:
                    print("ERROR: XLinks are not supported (" + value + ")")
                    continue
            plain_name = str(plain_name)
            if (isinstance(value, unicode)):
                value = str(value)
            self.__bindingInstance.SetFeature(plain_name, value)


    def contentHandler(self):
        """Reference to the xml.sax.handler.ContentHandler that is processing the document."""
        return self.__contentHandler
    __contentHandler = None

    def parentState(self):
        """Reference to the SAXElementState of the element enclosing this one."""
        return self.__parentState
    __parentState = None

    def setParentState(self, new_parentState):
        self.__parentState = new_parentState