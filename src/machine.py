import logging
from StringIO import StringIO
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

    def __str__(self):
        return self.printname()

    def __unicode__(self):
        return self.printname()

    def __repr__(self):
        return self.printname()

    def __eq__(self, other):
        # HACK this is only printname matching
        #return self.printname() == other.printname()
        return self.printname() == str(other)
    
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
        return set([self.__unicode__()]).union(*[partition[0].allNames() for partition in self.base.partitions[1:]])
        
    def append(self, what, which_partition=1):
        logging.debug(u"{0}.append({1},{2})".format(self.printname(),
                                                   what, which_partition))
        if len(self.base.partitions) > which_partition:
            if what in self.base.partitions[which_partition]:
                return
        self.base.append(what, which_partition)
        if isinstance(what, Machine):
            what.set_child_of(self, which_partition)

    def append_if_not_there(self, *args):
        logging.warning("old append_if_not_there() is now append(), " +
                        "use that instead")
        self.append(*args)

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

    """from now, only print and draw methots"""
    
    def to_dot(self, toplevel=False):
        s = u"subgraph"
        if toplevel:
            s = u"graph"
        
        s += u" cluster_{0}_{1} {{\n".format(self.base.partitions[0], id(self))
        s += u"label={0}_{1};\n".format(self.base.partitions[0], id(self))
        
        if len(self.base.partitions) > 1:
            s += "color=black;\n"
            for p in reversed(self.base.partitions[1:]):
                s += u"subgraph cluster_{0}_{1} {{\n".format(self.base.partitions[0], id(p))
                s += "label=\"\"\n"
                s += "color=lightgrey;\n"
                for m in reversed(p):
                    if isinstance(m, Machine):
                        s += m.to_dot()
                s += "}\n"
        else:
            #s += "color=white;\n"
            s += u"{0}[color=white, fontcolor=white];\n".format(self.base.partitions[0])
        s += "}\n"
        
        return s

    def to_full_str(self):
        """A more detailed __str__. Returns the print name,
        as well as the print names of the machines on every partition."""
        ret = str(self.base.partitions[0]) + ': '
        for p in self.base.partitions[1:]:
            ret += '[' + ','.join(str(m) for m in p) + '] '
        return ret
 
    @staticmethod
    def to_lisp_str(machine):
        """Returns the whole machine tree as a string."""
        s = StringIO()
        Machine.__to_lisp_str(s, machine, 0)
        return s.getvalue()

    @staticmethod
    def __to_lisp_str(out, machine, depth):
        """
        Recursive helper method for to_lisp_str().
        @param out the (unicode) output stream.
        @param machine the machine (or anything on a partition).
        @param depth the depth of @p machine in the machine tree.
        """
        indent = u' ' * depth * 4
        if type(machine) != Machine:
            out.write(u"{0}{1}\n".format(indent, machine))
            return

        out.write(u"{2}({0} : {1}\n".format(machine.printname(), hash(machine),
                                          indent))
        for i in xrange(1, len(machine.base.partitions)):
            out.write(u"{1}  {0}:[\n".format(i, indent))
            for m in machine.base.partitions[i]:
                Machine.__to_lisp_str(out, m, depth + 1)
            out.write(u"{0}  ]\n".format(indent))
        out.write(u"{0})\n".format(indent));

    @staticmethod
    def to_debug_str(machine):
        """An even more detailed __str__, complete with object ids and
        recursive."""
        return Machine.__to_debug_str(machine, 0)

    @staticmethod
    def __to_debug_str(machine, depth, lines=None, stop=None):
        """Recursive helper method for to_debug_str.
        @param depth the depth of the recursion.
        @param stop the machines already visited (to detect cycles)."""
        if stop is None:
            stop = set()
        if lines is None:
            lines = []

        if isinstance(machine, Machine):
            if machine in stop:
                lines.append('{0:>{1}}:{2}'.format(
                    str(machine), 2 * depth + len(str(machine)), id(machine)))
            else:
                stop.add(machine)
                lines.append('{0:>{1}}:{2}'.format(
                    str(machine), 2 * depth + len(str(machine)), id(machine)))
                for part in machine.base.partitions[1:]:
                    for m in part:
                        Machine.__to_debug_str(m, depth + 1, lines, stop)
        else:
            lines.append('{0:>{1}}'.format(
                    str(machine), 2 * depth + len(str(machine))))

        if depth == 0:
            return "\n".join(lines)

