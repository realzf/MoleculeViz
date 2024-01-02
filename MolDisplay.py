import molecule

#Header and footer for SVG output
header = """<svg version="1.1" width="1000" height="1000"
                   xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""

# Define offsets for the x and y coordinates in the SVG output
offsetx = 500
offsety = 500

# Declare dictionaries
radius = {}
element_name = {}

#Atom class representing an atom
class Atom:
    def __init__(self, c_atom):
        self.c_atom = c_atom
        self.z = c_atom.z

    def __str__(self):
            return f'Element: {self.c_atom.element}\nx: {self.c_atom.x}\ny: {self.c_atom.y}\nz: {self.z}'
    
    #Method to generate SVG code for the atom
    def svg(self):
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (
            self.c_atom.x * 100.0 + offsetx,
            self.c_atom.y * 100.0 + offsety,
            radius.get(self.c_atom.element),
            element_name[self.c_atom.element]
        )

#Bond class representing an bond   
class Bond:
    def __init__(self, c_bond):
          self.c_bond = c_bond
          self.z = c_bond.z

    def __str__(self):
        return (
                f'a1 index: {self.c_bond.a1}\na2 index: {self.c_bond.a2}\nepairs: {self.c_bond.epairs}\n'
                f'x1: {self.c_bond.x1}\ny1: {self.c_bond.y1}\nx2: {self.c_bond.x2}\ny2: {self.c_bond.y2}\n'
                f'len: {self.c_bond.len}\ndx: {self.c_bond.dx}\ndy: {self.c_bond.dy}'
        )

    #Method to generate SVG code for the bond
    def svg(self):

        #Compute points of rectangle connecting atoms
        x1 = self.c_bond.x1 * 100.0 + offsetx - self.c_bond.dy*10
        y1 = self.c_bond.y1 * 100.0 + offsety + self.c_bond.dx*10
        
        x2 = self.c_bond.x1 * 100.0 + offsetx + self.c_bond.dy*10
        y2 = self.c_bond.y1 * 100.0 + offsety - self.c_bond.dx*10 

        x3 = self.c_bond.x2 * 100.0 + offsetx + self.c_bond.dy*10
        y3 = self.c_bond.y2 * 100.0 + offsety - self.c_bond.dx*10
        
        x4 = self.c_bond.x2 * 100.0 + offsetx - self.c_bond.dy*10
        y4 = self.c_bond.y2 * 100.0 + offsety + self.c_bond.dx*10

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x1, y1, x2, y2, x3, y3, x4, y4)

#Molecule class representing a molecule 
class Molecule(molecule.molecule):
    def __str__(self):
        string = ""

        string += "ATOMS:\n"
        for i in range(self.atom_no):
            atom = Atom(self.get_atom(i)) 
            string += atom.__str__()
            string += "\n\n"

        string += "\nBONDS:\n"
        for i in range(self.bond_no): 
            bond = Bond(self.get_bond(i))
            string += bond.__str__()
            string += "\n\n"

        return string
    
    #Method to create SVG code for a molecule
    def svg(self):
        countAtoms = 0
        countBonds = 0

        #SVG header
        string = header

        while countAtoms != self.atom_no and countBonds != self.bond_no:
            #Create Atom/Bond object for Molecule object    
            atom = Atom(self.get_atom(countAtoms))
            bond = Bond(self.get_bond(countBonds))

            #Check which has a smaller z-coordinate and add it to the overall string first
            if atom.z < bond.z:
                string += atom.svg()
                countAtoms += 1

            else:
                string += bond.svg()
                countBonds += 1   

        
        #Add any remaining atoms or bonds to the overall string
        if countAtoms != self.atom_no:
            while countAtoms != self.atom_no:
                atom = Atom(self.get_atom(countAtoms))
                string += atom.svg()
                countAtoms += 1

        else:
            while countBonds != self.bond_no:
                bond = Bond(self.get_bond(countBonds))
                string += bond.svg()
                countBonds += 1   
                
        #SVG footer
        string += footer
        
        return string

    #Method for parsing sdf files 
    def parse(self, file):
        for i in range (3):
            file.readline()

        line = file.readline().split()

        #Get number of atoms and bonds
        numAtoms = int(line[0])
        numBonds = int(line[1])
        
        #Parse atom and bond information into Molecule 
        for i in range (numAtoms):
            line = file.readline().split()
            self.append_atom(line[3], float(line[0]), float(line[1]), float(line[2]))
            
        for i in range (numBonds):
            line = file.readline().split()
            self.append_bond(int(line[0]) - 1, int(line[1]) - 1, int(line[2]))
