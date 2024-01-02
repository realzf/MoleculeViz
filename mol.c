/**
 * Programmer: Zaeem Farhan
 * Course: CIS*2750 A4
 * Assignment: Molecule Manipulation Library
 * Date: April 1 2023
 * Description: This C file contains the functions definitions for the libmol library
 */

#include "mol.h"

/*
 * Function: atomset
 * ----------------------------
 *   Copies the values pointed to by element, x, y, and z into the atom stored at atom
 *
 *   *atom: atom which is copying the values
 *   element: Element name
 *   *x: x value
 *   *y: y value
 *   *z: z value
 *
 *   returns: void
 */
void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
    strcpy(atom->element, element);
}

/*
 * Function: atomget
 * ----------------------------
 *   Copies the values in the atom stored at atom to the locations pointed to by
 *   element, x, y, and z.
 *
 *   *atom: atom which stores the values to be copied
 *   element: Element name
 *   *x: x value
 *   *y: y value
 *   *z: z value
 *
 *   returns: void
 */
void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

/*
 * Function: bondset
 * ----------------------------
 *   Copies the values a1, a2 and epairs into the corresponding structure attributes in bond
 *
 *   *bond: bond struct
 *   *a1: atom in bond
 *   *a2: second atom in bond
 *   epairs: number of electron pairs
 *   **atoms: array of atoms
 * 
 *   returns: void
 */
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;
    compute_coords(bond);
}

/*
 * Function: bondget
 * ----------------------------
 *   Copies  the structure attributes in bond to their corresponding arguments: 
 *   a1, a2 and epairs.
 *
 *   *bond: bond struct
 *   *a1: index of a1 in atoms array
 *   *a2: index of a2 in atoms array
 *   **atoms: array containing atoms
 *   *epairs: number of electron pairs  
 * 
 *   returns: void
 */
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
}

/*
 * Function: compute_coords
 * ----------------------------
 *    Computes the z, x1, y1, x2, y2, len, dx, and dy values of the bond and set
 *    them in the appropriate structure member variables
 *    
 *    *bond: bond structure to be set
 * 
 *    returns: void
 */
void compute_coords( bond *bond ){
    //set x and y values of first atom
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;

    //set x and y values of second atom
    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    //set z value (average z value of a1 and a2)
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2.0;

    //compute len, dx and dy
    bond->len = sqrt(pow((bond->x2 - bond->x1), 2) + pow((bond->y2 - bond->y1), 2));

    if(bond->x2 != bond->x1){
        bond->dx = (bond->x2 - bond->x1) / bond->len;
    }else{
        bond->dx = 0;
    }
    
    if(bond->y2 != bond->y1){
        bond->dy = (bond->y2 - bond->y1) / bond->len;
    }else{
        bond->dy = 0;
    }
}


/*
 * Function: molmalloc
 * ----------------------------
 *    Creates and allocates memory for a new molecule
 *
 *    atom_max: max number of atoms
 *    bond_max: max number of bonds
 * 
 *    returns: returns the address of a malloced area of memory
 */
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max){
    molecule *temp = malloc(sizeof(struct molecule));

    //all if statements for error allocating memory
    if(temp == NULL){
        fprintf(stderr, "Error allocating memory.");
        return NULL;
    }

    temp->atoms = malloc(sizeof(struct atom) * atom_max);
    if(temp->atoms == NULL){
        free(temp);
        fprintf(stderr, "Error allocating memory.");
        return NULL;
    }

    temp->atom_ptrs = malloc(sizeof(struct atom*) * atom_max);
    if(temp->atom_ptrs == NULL){
        free(temp->atoms);
        free(temp);
        fprintf(stderr, "Error allocating memory.");
        return NULL;
    }

    temp->atom_no = 0;
    temp->atom_max = atom_max;
    
    temp->bonds = malloc(sizeof(struct bond) * bond_max);
    if(temp->bonds == NULL){
        free(temp->atoms);
        free(temp->atom_ptrs);
        free(temp);
        fprintf(stderr, "Error allocating memory.");
        return NULL;
    }

    temp->bond_ptrs = malloc(sizeof(struct bond *) * bond_max);
    if(temp->bond_ptrs == NULL){
        free(temp->atoms);
        free(temp->atom_ptrs);
        free(temp->bonds);
        free(temp);
        fprintf(stderr, "Error allocating memory.");
        return NULL;
    }

    temp->bond_no = 0;
    temp->bond_max = bond_max;
    return temp;
}

/*
 * Function: molappend_atom
 * ----------------------------
 *    Copies the data pointed to by atom to the first “empty” atom in atoms in the
 *    molecule pointed to by molecule, and set the first “empty” pointer in atom_ptrs 
 *    to the same atom in the atoms array.
 *
 *    *molecule: molecule in which the atom is added to
 *    *atom: atom to be appended to *molecule 
 * 
 *    returns: void
 */
void molappend_atom( molecule *molecule, atom *atom ){
    struct atom *temp1, **temp2;
    
    if(molecule == NULL || atom == NULL){
        exit(1);
    }

    //incase more memory is needing to be allocated for atoms
    if(molecule->atom_no == molecule->atom_max){
        if(molecule->atom_max < 1){
            molecule->atom_max = 1;

        }else{
            molecule->atom_max = molecule->atom_max * 2;
        }
       
        temp1 = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        temp2 = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);

        if(temp1 == NULL){
            free(temp2);
            fprintf(stderr, "Error allocating memory.");
            exit(1);

        }else if(temp2 == NULL){
            free(temp1);
            fprintf(stderr, "Error allocating memory.");
            exit(1);
        }

        molecule->atoms = temp1;
        molecule->atom_ptrs = temp2;

        for (int i = 0; i < molecule->atom_no; i++){
            molecule->atom_ptrs[i] = &(molecule->atoms[i]);
        }
    }

    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);
    molecule->atom_no++;
}

/*
 * Function: molappend_bond
 * ----------------------------
 *    Copies the data pointed to by bond to the first “empty” bond in bonds in the
 *    molecule pointed to by molecule, and set the first “empty” pointer in bond_ptrs 
 *    to the same bond in the bonds array.
 *
 *    *molecule: molecule in which the bond is added to
 *    *bond: bond to be appended to *molecule 
 * 
 *    returns: void
 */
void molappend_bond( molecule *molecule, bond *bond ){
    if(molecule == NULL || bond == NULL){
        exit(1);
    }

    //incase more memory needs to be allocated for bonds
    if(molecule->bond_max == molecule->bond_no){
        if(molecule->bond_max < 1){
            molecule->bond_max = 1;

        }else{
            molecule->bond_max = molecule->bond_max * 2;
        }
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);

        for (int i = 0; i < molecule->bond_no; i++){
            molecule->bond_ptrs[i] = &(molecule->bonds[i]);
        }
    }

    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    molecule->bond_no++;
}

/*
 * Function: molcopy
 * ----------------------------
 *    Creates and allocates memory for a new and exact same molecule as *src
 *
 *    *src: new molecule stores data from *src molecule
 * 
 *    returns: void
 */
molecule *molcopy( molecule *src ){
    if(src == NULL){
        exit(1);
    }

    molecule * mol = molmalloc(src->atom_max, src->bond_max);

    if(mol == NULL){
        fprintf(stderr, "Error allocating memory.");
        return NULL;
    }
    
    for(int i = 0; i < src->atom_no; i++){
        molappend_atom(mol, &src->atoms[i]);
    }

    for(int i = 0; i < src->bond_no; i++){
        molappend_bond(mol, &src->bonds[i]);
    }
    return mol;
}

/*
 * Function: atoms_cmp
 * ----------------------------
 *    Used for qsort in molsort function to sort atoms
 */
int atoms_cmp(const void *a, const void *b){
    atom *a_ptr = *(atom**) a;
    atom *b_ptr = *(atom**) b;

    if(a_ptr->z > b_ptr->z){
        return 1;

    }else if(a_ptr->z < b_ptr->z) {
        return -1;
        
    }else {
        return 0;
    }
}

/*
 * Function: bond_cmp
 * ----------------------------
 *    Used for qsort in molsort function to sort bonds
 */
int bond_comp( const void *a, const void *b ){
    bond *a_ptr = *(bond**) a;
    bond *b_ptr = *(bond**) b;

    if((a_ptr->z + a_ptr->z) > (b_ptr->z + b_ptr->z)){
        return 1;

    }else if((a_ptr->z + a_ptr->z) < (b_ptr->z + b_ptr->z)) {
        return -1;

    }else {
        return 0;
    }
}

/*
 * Function: molsort
 * ----------------------------
 *    Sorts the atom_ptrs array in place in order of increasing z value. I.e.
 *    atom_ptrs[0] should point to the atom that contains the lowest z value and
 *    atom_ptrs[atom_no-1] should contain the highest z value. Also sorts the bond_ptrs
 *    array in place in order of increasing “z value”. The z value is assumed 
 *    to be the average z value of their two atoms.
 * 
 *    *molecule: atoms_ptrs and bond_ptrs in this molecule are sorted
 * 
 *    returns: void
 */
void molsort( molecule *molecule ){
    if(molecule == NULL){
        exit(1);
    }

    //sort using qsort
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), atoms_cmp);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), bond_comp);
}

/*
 * Function: xrotation
 * ----------------------------
 *    This function sets the values in an affine transformation matrix, 
 *    xform_matrix, corresponding to a rotation of deg degrees around the x-axis
 * 
 *    xform_matrix: 3-D affine transformation matrix
 *    deg: degrees of rotation
 * 
 *    returns: void
 */
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
    //convert degrees to radians
    double radians = deg * PI / 180.0;
    
    //computation for rotation
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(radians);
    xform_matrix[1][2] = -sin(radians);
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(radians);
    xform_matrix[2][2] = cos(radians);
}

/*
 * Function: yrotation
 * ----------------------------
 *    This function sets the values in an affine transformation matrix, 
 *    xform_matrix, corresponding to a rotation of deg degrees around the y-axis
 * 
 *    xform_matrix: 3-D affine transformation matrix
 *    deg: degrees of rotation
 * 
 *    returns: void
 */
void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    //convert degrees to radians
    double radians = deg * PI / 180.0;

    //computation for rotation
    xform_matrix[0][0] = cos(radians);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(radians);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sin(radians);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(radians);
}

/*
 * Function: zrotation
 * ----------------------------
 *    This function sets the values in an affine transformation matrix, 
 *    xform_matrix, corresponding to a rotation of deg degrees around the z-axis
 * 
 *    xform_matrix: 3-D affine transformation matrix
 *    deg: degrees of rotation
 * 
 *    returns: void
 */
void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    //convert degrees to radians
    double radians = deg * PI / 180.0;

    //computation for rotation
    xform_matrix[0][0] = cos(radians);
    xform_matrix[0][1] = -sin(radians);
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(radians);
    xform_matrix[1][1] = cos(radians);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

/*
 * Function: mol_xform
 * ----------------------------
 *    This function will apply the transformation matrix to all the atoms of the molecule by
 *    performing a vector matrix multiplication on the x, y, z coordinates.
 * 
 *    *molecule: molecule which the all atoms/ x, y and z values will be transformed
 *    matrix: matrix representing a 3-d affine transformation matrix 
 * 
 *    returns: void
 */
void mol_xform( molecule *molecule, xform_matrix matrix ){
    double x, y ,z;

    if(molecule == NULL){
        exit(1);
    }
    
    //matrix multiplication
    for (int i = 0; i < molecule->atom_no; i++){
        x = molecule->atoms[i].x;
        y = molecule->atoms[i].y;
        z = molecule->atoms[i].z;

        molecule->atoms[i].x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z;
        molecule->atoms[i].y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z;
        molecule->atoms[i].z = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z;
    }

    molecule->bonds->atoms = molecule->atoms;
    
    //set transformed x, y, z values
    for (int i = 0; i < molecule->bond_no; i++){
        compute_coords(&molecule->bonds[i]);
    }
}

/*
 * Function: molfree
 * ----------------------------
 *    Frees memory for molecules
 * 
 *    returns: void
 */
void molfree( molecule *ptr ){
    if(ptr->atoms != NULL){
        free(ptr->atoms);
    }

    if(ptr->atom_ptrs != NULL){
        free(ptr->atom_ptrs);
    }

    if(ptr->bonds != NULL){
        free(ptr->bonds);
    }

    if(ptr->bond_ptrs != NULL){
        free(ptr->bond_ptrs);
    }

    if(ptr != NULL){
        free(ptr);
    }
}

