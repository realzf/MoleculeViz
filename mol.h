/**
 * Programmer: Zaeem Farhan
 * Course: CIS*2750 A4
 * Assignment: Molecule Manipulation Library
 * Date: Aptil 1 2023
 * Description: This header file contains structure definitions and function prototypes 
*/

#ifndef _mol_h
#define _mol_h

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.1415926535897932384626433832795028841

//Atom structure that describes an atom and its position in 3-dimensional space
typedef struct atom{
    char element[3];
    double x, y, z;
} atom;

//Bond structure that represents a co-valent bond between two atoms
typedef struct bond{
    unsigned short a1, a2;
    unsigned char epairs;
    atom *atoms;
    double x1, x2, y1, y2, z, len, dx, dy;
} bond;

//Struct molecule represents a molecule which consists of zero or more atoms, and zero or more bonds
typedef struct molecule{
    unsigned short atom_max, atom_no;
    atom *atoms, **atom_ptrs;
    unsigned short bond_max, bond_no;
    bond *bonds, **bond_ptrs;
} molecule;

//3-D affine transformation matrix
typedef double xform_matrix[3][3];

/*
typedef struct mx_wrapper
{
  xform_matrix xform_matrix;
} mx_wrapper;

typedef struct rotations
{
  molecule *x[72];
  molecule *y[72];
  molecule *z[72];
} rotations;
*/

//Function definitions
void atomset( atom *atom, char element[3], double *x, double *y, double *z );
void atomget( atom *atom, char element[3], double *x, double *y, double *z );
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
void compute_coords( bond *bond );
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max);
molecule *molcopy( molecule *src );
void molfree( molecule *ptr );
void molappend_atom( molecule *molecule, atom *atom );
void molappend_bond( molecule *molecule, bond *bond );
void molsort( molecule *molecule );
void xrotation( xform_matrix xform_matrix, unsigned short deg );
void yrotation( xform_matrix xform_matrix, unsigned short deg );
void zrotation( xform_matrix xform_matrix, unsigned short deg );
void mol_xform( molecule *molecule, xform_matrix matrix );
int atoms_cmp( const void *a, const void *b );
int bond_comp( const void *a, const void *b );
//rotations *spin( molecule *mol );
//void rotationsfree( rotations *rotations );

#endif
