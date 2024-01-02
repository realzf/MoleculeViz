import os
import sqlite3
import MolDisplay

#Class used for modifying SQLLite database
class Database:
    def __init__(self, reset):
        #Remove old database file 
        if reset == True:
            if os.path.exists('molecules.db'):
                os.remove('molecules.db')

        #Connect to database file
        self.conn = sqlite3.connect('molecules.db')

    #Creates all tables for the database
    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements
                           (ELEMENT_NO INTEGER NOT NULL,
                            ELEMENT_CODE VARCHAR(3) NOT NULL,
                            ELEMENT_NAME VARCHAR(32) NOT NULL,
                            COLOUR1 CHAR(6) NOT NULL,
                            COLOUR2 CHAR(6) NOT NULL,
                            COLOUR3 CHAR(6) NOT NULL,
                            RADIUS DECIMAL(3) NOT NULL,
                            PRIMARY KEY(ELEMENT_CODE))""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
                           (ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            ELEMENT_CODE VARCHAR(3) NOT NULL,
                            X DECIMAL(7,4) NOT NULL,
                            Y DECIMAL(7,4) NOT NULL,
                            Z DECIMAL(7,4) NOT NULL,
                            FOREIGN KEY(ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE))""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
                           (BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            A1 INTEGER NOT NULL,
                            A2 INTEGER NOT NULL,
                            EPAIRS INTEGER NOT NULL)""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
                           (MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            NAME TEXT UNIQUE NOT NULL)""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                           (MOLECULE_ID INTEGER NOT NULL,
                            ATOM_ID INTEGER NOT NULL,
                            PRIMARY KEY(MOLECULE_ID, ATOM_ID),
                            FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                            FOREIGN KEY(ATOM_ID) REFERENCES Atoms(ATOM_ID))""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                           (MOLECULE_ID INTEGER NOT NULL,
                            BOND_ID INTEGER NOT NULL,
                            PRIMARY KEY(MOLECULE_ID, BOND_ID),
                            FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                            FOREIGN KEY(BOND_ID) REFERENCES Bonds(BOND_ID))""")
        self.conn.commit()

    #Used for Inserting data into specific tables
    def __setitem__( self, table, values ):
        cursor = self.conn.cursor()

        if table == 'Elements':
            cursor.execute("INSERT INTO Elements (ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS) VALUES (?, ?, ?, ?, ?, ?, ?)", values)
        
        elif table == 'Atoms':
            cursor.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)", values)
        
        elif table == 'Bonds':
            cursor.execute("INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", values)
        
        elif table == 'Molecules':
            cursor.execute("INSERT OR REPLACE INTO Molecules (NAME) VALUES (?)", values)
        
        elif table == 'MoleculeAtom':
            cursor.execute("INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)", values)
        
        elif table == 'MoleculeBond':
            cursor.execute("INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)", values)
        
        self.conn.commit()

    #Adds an atom to the database
    def add_atom(self, molname, atom):
        cursor = self.conn.cursor()
        self['Atoms'] = (atom.element, atom.x, atom.y, atom.z)
        
        #Gets last atom id from Atoms table
        result = cursor.execute("SELECT MAX(ATOM_ID)FROM Atoms")
        atom_id = result.fetchone()[0]
        
        #Update foreign keys
        cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,))
        molecule_id = cursor.fetchone()[0]
        self['MoleculeAtom'] = (molecule_id, atom_id)

    #Adds a bond to the database
    def add_bond(self, molname, bond):
        cursor = self.conn.cursor()
        self['Bonds'] = (bond.a1, bond.a2, bond.epairs)

        #Gets last bond id from Bonds table
        result = cursor.execute("SELECT MAX(BOND_ID)FROM Bonds")
        bond_id = result.fetchone()[0]

        #Update foreign keys
        cursor.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,))
        molecule_id = cursor.fetchone()[0]

        self['MoleculeBond'] = (molecule_id, bond_id)

    #Adds a molecule to the database
    def add_molecule(self, name, fp):
        self['Molecules'] = (name,)
        
        mol = MolDisplay.Molecule()
        mol.parse(fp)

        #Adds every atom to the database        
        for i in range(mol.atom_no):
            atom = mol.get_atom(i)
            self.add_atom(name, atom)

        #Adds every bond to the database            
        for i in range(mol.bond_no):
            bond = mol.get_bond(i)
            self.add_bond(name, bond)

    #Used to load a molecule from the database
    def load_mol(self, name):
        mol = MolDisplay.Molecule()
        cursor = self.conn.cursor()

        #Fetches all info needed to append an atom
        atoms = cursor.execute("""SELECT Elements.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z 
                                    FROM Molecules 
                                    JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID 
                                    JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID 
                                    JOIN Elements ON Atoms.ELEMENT_CODE = Elements.ELEMENT_CODE 
                                    WHERE Molecules.NAME = ? 
                                    ORDER BY Atoms.ATOM_ID ASC""", (name,)).fetchall()
        self.conn.commit()

        for row in atoms:
            element, x, y, z = row
            mol.append_atom(element, x, y, z)

        #Fetches all info needed to append an bond
        bonds = cursor.execute("""SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS 
                                    FROM Molecules 
                                    JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID 
                                    JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID 
                                    WHERE Molecules.NAME = ? 
                                    ORDER BY Bonds.BOND_ID ASC""", (name,)).fetchall()
        self.conn.commit()

        for row in bonds:
            a1, a2, epairs = row
            mol.append_bond(a1, a2, epairs)

        return mol

    #Returns radius dicitonary for each element
    def radius(self):
        cursor = self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements")
        rows = cursor.fetchall()

        radius_dict = {row[0]: row[1] for row in rows}
        return radius_dict
    
    #Returns a dictionary containing all element names and elements codes
    def element_name(self):
        cursor = self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")
        rows = cursor.fetchall()

        element_name_dict = {row[0]: row[1] for row in rows}
        return element_name_dict

    #Returns svg code for the svg file
    def radial_gradients(self):
        cursor = self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")
        rows = cursor.fetchall()

        radial_gradients_str = ""
        radialGradientSVG = """
        <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
        <stop offset="0%%" stop-color="%s"/>
        <stop offset="50%%" stop-color="%s"/>
        <stop offset="100%%" stop-color="%s"/>
        </radialGradient>"""

        for row in rows:
            element_name = row[0]
            colour1 = row[1]
            colour2 = row[2]
            colour3 = row[3]
            radial_gradient = radialGradientSVG % (element_name, colour1, colour2, colour3)
            radial_gradients_str += radial_gradient

        return radial_gradients_str