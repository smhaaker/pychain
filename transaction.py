from collections import OrderedDict
#from printable import Printable
from util.printable import Printable

class Transaction(Printable):
    """ Transaction to be added to blockchain block
    
    Attributes:
        :sender: sender
        :recipient: recipient
        :signature: transaction signature
        :amount: value
    """

    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender),('recipient', self.recipient),('amount', self.amount)])