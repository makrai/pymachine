import logging

class Monoid:
    """
    Our monoid class
    """
    
    def __init__(self, name):
        self.partitions = []
        self.partitions.append(name)
        
        self.operations = None
        self.unit = None
        self.distinguished_partition = None
    
    def __str__(self):
        return self.partitions[0]
    
    def __eq__(self, other):
        return (self.partitions == other.partitions and
                self.operations == other.operations and
                self.unit == other.unit and
                self.distinguished_partition == other.distinguished_partition)

    def append(self, which_partition, what):
        if len(self.partitions) > which_partition:
            from machine import Machine
            if isinstance(what, Machine):
                self.partitions[which_partition].append(what)
            else:
                raise TypeError("Only machines can be added to partitions")
        else:
            while len(self.partitions) <= which_partition:
                self.partitions.append([])
            self.partitions[which_partition].append(what)
            #raise IndexError("That partition does not exist")

