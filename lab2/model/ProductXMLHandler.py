class ProductXMLHandler(xml.sax.ContentHandler):
    """SAX обработчик для загрузки XML"""
    
    def __init__(self):
        super().__init__()
        self.products = []
        self.current_product = {}
        self.current_tag = ""
        
    def startElement(self, tag, attrs):
        self.current_tag = tag
        if tag == 'product':
            self.current_product = {}
            
    def endElement(self, tag):
        if tag == 'product':
            self.products.append(Product(
                name=self.current_product.get('name', ''),
                manufacturer=self.current_product.get('manufacturer', ''),
                unp=self.current_product.get('unp', ''),
                quantity=int(self.current_product.get('quantity', 0)),
                address=self.current_product.get('address', '')
            ))
            
    def characters(self, content):
        if self.current_tag and content.strip():
            self.current_product[self.current_tag] = content.strip()
