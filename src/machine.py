import logging
import copy

from monoid import Monoid
import control as ctrl

class Machine(object):
    def __init__(self, base, control=None):
        
        self.set_control(control)
        
        # base is a monoid
        if not isinstance(base, Monoid):
            raise TypeError("base should be a Monoid instance")
        self.base = base

        self._child_of = set()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.printname()

    def __eq__(self, other):
        # HACK this is only printname matching
        return unicode(self) == unicode(other)
    
    def __hash__(self):
        # HACK
        return hash(self.printname())

    def __deepcopy__(self, memo):
        new_machine = self.__class__(Monoid("anyad"))
        memo[id(self)] = new_machine
        new_base = copy.deepcopy(self.base, memo)
        new_control = copy.deepcopy(self.control, memo)
        new_machine.base = new_base
        new_machine.control = new_control

        for part_i, part in enumerate(new_base.partitions[1:]):
            part_i += 1
            for m in part:
                if isinstance(m, Machine):
                    m.set_child_of(new_machine, part_i)
        return new_machine

    def printname(self):
        return self.base.partitions[0]

    def set_control(self, control):
        """Sets the control."""
        # control will be an FST representation later
        if not isinstance(control, ctrl.Control) and control is not None:
            raise TypeError("control should be a Control instance")
        self.control = control
        if control is not None:
            control.set_machine(self)

    def allNames(self):
        return set([self.__unicode__()]).union(*[partition[0].allNames()
            for partition in self.base.partitions[1:]])
        
    def append(self, what, which_partition=1):
        logging.debug(u"{0}.append({1},{2})".format(self.printname(),
           unicode(what), which_partition).encode("utf-8"))
        if len(self.base.partitions) > which_partition:
            if what in self.base.partitions[which_partition]:
                return
        else:
            self.base.partitions += [[]] * (which_partition + 1 -
                len(self.base.partitions))
        self.base.append(what, which_partition)
        if isinstance(what, Machine):
            what.set_child_of(self, which_partition)

    def set_child_of(self, whose, part):
        self._child_of.add((whose, part))

    def del_child_of(self, whose, part):
        self._child_of.remove((whose, part))

    def remove(self, what, which_partition=None):
        """Removes @p what from the specified partition. If @p which_partition
        is @c None, @p what is removed from all partitions on which it is
        found."""
        self.base.remove(what, which_partition)
        if isinstance(what, Machine):
            what.del_child_of(self, which_partition)

    def search(self, what=None, empty=False):
        results = []
        for part_i, part in enumerate(self.base.partitions[1:]):
            if empty:
                if len(part) == 0:
                    results.append((self, part_i + 1))
            for m in part:
                if what is not None:
                    if m.base.partitions[0] == what:
                        results.append((self, part_i + 1))
                results += m.search(what=what, empty=empty)
        return results

    @staticmethod
    def to_debug_str(machine):
        """An even more detailed __str__, complete with object ids and
        recursive."""
        if isinstance(machine, Machine):
            return machine.__to_debug_str(0)
        else:
            return ('{0:>{1}}'.format(
                    str(machine), len(str(machine))))

    def __to_debug_str(self, depth, lines=None, stop=None):
        """Recursive helper method for to_debug_str.
        @param depth the depth of the recursion.
        @param stop the machines already visited (to detect cycles)."""
        if stop is None:
            stop = set()
        if lines is None:
            lines = []

        # TO BE DELETED
        if isinstance(self, Machine):
            if self in stop:
                lines.append('{0:>{1}}:{2}'.format(
                    str(self), 2 * depth + len(str(self)), id(self)))
            else:
                stop.add(self)
                lines.append('{0:>{1}}:{2}'.format(
                    str(self), 2 * depth + len(str(self)), id(self)))
                for part in self.base.partitions[1:]:
                    for m in part:
                        m.__to_debug_str(depth + 1, lines, stop)
        else:
            lines.append('{0:>{1}}'.format(
                    str(self), 2 * depth + len(str(self))))

        if depth == 0:
            return "\n".join(lines)

def test_printname():
    m_unicode = Machine(Monoid(u"\u00c1"))
    print unicode(m_unicode).encode("utf-8")
    print str(m_unicode)
    logging.error(unicode(m_unicode).encode("utf-8"))


if __name__ == "__main__":
    test_printname()
