#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2017-05-30

from __future__ import division # MUST be run before all other expressions , including docstrings!

"""
OGLshapes.py
James Watson , 2017 August , Written on Spyder 3 / Python 2.7
Primitive shapes and meshes to display in Pyglet / OpenGL 

Dependencies: numpy , pyglet
"""

"""
~~~~~ Development Plan ~~~~~

[ ] Vector array optimization ( See Drawable )

"""

# === Init =================================================================================================================================

# ~~ Helpers ~~


# ~~ Imports ~~
# ~ Standard ~
from math import sqrt
# ~ Special ~
import numpy as np
import pyglet # --------- Package for OpenGL
#- OpenGL flags and state machine
from pyglet.gl import ( GL_LINES , glColor3ub , GL_TRIANGLES , glTranslated , GL_QUADS , glRotated , glClearColor , glEnable , GL_DEPTH_TEST , 
                        glMatrixMode , GL_PROJECTION , glLoadIdentity , gluPerspective , GL_MODELVIEW , gluLookAt , GL_POINTS , glPointSize )
# from pyglet import clock # Animation timing ( Not sure why would prefer this over vanilla Python timing? )
# ~ Local ~
from marchhare import build_sublists_by_cadence , flatten_nested_sequence , concat_arr
from Vector import vec_unit , vec_mag
from VectorMath.Vector3D import apply_homog , homogeneous_Z , homog_ang_axs 

# ~~ Setup ~~

# ___ End Init _____________________________________________________________________________________________________________________________

# == Helper Functions ==

def generate_segment_indices_for_OGmesh( pF , Fcadence = 3 ):
    """ Obtain indices for line segments connecting vertices at facet edges , without interior segments or repeats """
    def pairs_eq( pair1 , pair2 ):
        """ Determine if two pairs have the same elements """
        return ( ( pair1[0] == pair2[0] ) and ( pair1[1] == pair2[1] ) ) or ( ( pair1[0] == pair2[1] ) and ( pair1[1] == pair2[0] ) )
    def pair_in_list( pair , pairList ):
        """ Determine if 'pair' is in 'ls' """
        for testPair in pairList:
            if pairs_eq( testPair , pair ):
                return True
        return False
    F = build_sublists_by_cadence( pF , Fcadence ) # This function probably doesn't work for cadence other than 3 , see 'triPairs'
    usedPairs = []
    triPairs  = ( ( 0 , 1 ) , ( 1 , 2 ) , ( 2 , 0 ) )
    # 1. For each facet in the mesh
    for f_i in F:
        # 2. Get all three segments as pairs of V indices
        fPairs = [ [ f_i[ triPairs[i][j] ] for j in xrange( 2 ) ] for i in xrange( len( triPairs ) ) ]
        # 3. For each index pair
        for pair in fPairs:
            # 4. Check the used list to see if this pair has been used
            if not pair_in_list( pair , usedPairs ):
                # 5. If the pair has not been used , append the pair to the list
                usedPairs.append( pair )
    return flatten_nested_sequence( usedPairs )
        
        

# __ End Helper __

# ==== OpenGL Classes ====
        
# === Drawable Classes ===

# == class OGLDrawable ==

class OGLDrawable( object ):
    """ Template class for drawing rigid objects in Pyglet and performing rigid transformations """
    
    def __init__( self , cntr = [ 0 , 0 , 0 ] ):
        """ Instantiate a drawable object with its 'cntr' specified in the parent frame """
        self.pos3D = cntr # ------------------- Position of the object in the
        self.drawOffset = [ 0.0 , 0.0 , 0.0 ] # Vector to subtract from vertices
        self.vertices = () # ------------------ Tuple of vertices that define the drawable geometry
        self.vertX = list( self.vertices ) # -- List of transformed vertices
        self.indices = () # ------------------- Tuple of indices of 'vertX' that determine the which are used to draw what parts of the geometry
        self.trnsByOGL = False # -------------- Flag for whether to apply translation by OpenGL: True - OpenGL , False - Matrix Algebra
        self.rotnByOGL = False # -------------- Flag for whether to apply rotation by OpenGL: True - OpenGL , False - Matrix Algebra
        self.colors = ( ( 255 , 255 , 255 ) ) # All of the colors used to paint the object
        self.thetaDeg = 0.0 # ----------------- Rotation angle for OGL transform [deg]
        self.thetaRad = 0.0 # ----------------- Rotation angle for OGL transform [rad , must be converted]
        self.rotAxis = [ 0.0 , 0.0 , 1.0 ] # -- Rotation axis for OGL transform # TODO: Find out if this has to be normalized!

    def add_vertex_offset( self , offset = [] ):
        """ Calc the relative positions of vertices given the center , Set a new offset if specified """
        if len( offset ) == 3:
            self.drawOffset = offset
        self.vertices = list( self.vertices )
        for i in xrange( 0 , len( self.vertices ) , 3 ):
            self.vertices[ i : i+3 ] = np.add( self.vertices[ i : i+3 ] , self.drawOffset )
        self.vertices = tuple( self.vertices )
        
    def set_offset( self , offset ):
        """ Set center to that specified , Calc the relative positions of vertices given the center """
        self.calc_verts_rela( offset )
        
    def xform_homog( self , homogXform ):
        """ Transform all of the vertices with 'homogXform' (4x4) and store the result for rendering """
        for i in xrange( 0 , len( self.vertices ) , 3 ):
            # print "DEBUG :" , self.vertices[ i : i+3 ]
            self.vertX[ i : i+3 ] = apply_homog( homogXform , self.vertices[ i : i+3 ] )
    
    def xform_Z_rot( self , thetaZrad ):
        """ Rotate all of the vertices in the list about the local Z axis """
        self.xform_homog( homogeneous_Z( thetaZrad , [ 0 , 0 , 0 ] ) )
        
    def xform_ang_axs( self , thetaRad , k ):
        """ Rotate all of the vertices in the list about the local Z axis """
        self.xform_homog( homog_ang_axs( thetaRad , k , [ 0 , 0 , 0 ] ) )

    def state_transform( self ):
        """ Set the transformation matrix in the OGL state machine for this object """
        # If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        if self.trnsByOGL: # Translate first
            glTranslated( *self.pos3D ) # This moves the origin of drawing , so that we can use the above coordinates at each draw location
        if self.rotnByOGL: # Rotate last
            glRotated( self.thetaDeg , *self.rotAxis )
            
    def state_untransform( self ):
        """ Unset the transformation matrix in the OGL state machine for this object , so that other shapes can set it for themselves """
        # If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        if self.rotnByOGL: # Unrotate first
            glRotated( -self.thetaDeg , *self.rotAxis )
        if self.trnsByOGL: # Untranslate last
            glTranslated( *np.multiply( self.pos3D , -1 ) ) # Reset the transform coordinates

    def draw( self ): # VIRTUAL
        """ Render the INHERITED_CLASS """
        raise NotImplementedError( "OVERRIDE: YOU RAN THE INHERITED VIRTUAL VERSION OF THE 'draw' function!" ) 
        # ~~ Implementation Template ~~
        # [1]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        # self.state_transform()
        # [2]. Set color , size , and shape-specific parameters
        # glColor3ub( *self.colors[0] ) 
        # [3]. Render! 
        # pyglet.graphics.draw_indexed( 
        #     10 , # ----------------- Number of seqential triplet in vertex list
        #     GL_LINES , # ----------- Draw quadrilaterals
        #     self.vectors[i] , # ---- Indices where the coordinates are stored
        #     ( 'v3f' , self.vertX ) # vertex list , OpenGL offers an optimized vertex list object , but this is not it
        # )
        # [4]. If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        # self.state_untransform()
        
# __ end OGLDrawable __


# == class Point ==
     
class Point_OGL( OGLDrawable ):
    """ Visible representation of a 1D point """
    
    def __init__( self , pnt = [ 0 , 0 , 0 ] , size = 8 , color = ( 255 , 255 , 255 ) ):
        """ Define a single point """
        OGLDrawable.__init__( self , pnt ) # - Parent class init
        self.vertices = tuple( pnt ) # ------- Tuple of vertices that define the drawable geometry
        self.vertX = list( self.vertices ) # - List of transformed vertices
        self.indices = tuple( [ 0 ] ) # ------ Tuple of indices of 'vertX' that determine the which are used to draw what parts of the geometry
        self.size = size # ------------------- Width of point marker
        self.colors = ( [ tuple( color ) ] ) # Point marker color
        
    def set_pos( self , pos ):
        """ Set the position of the point """
        self.vertices = tuple( pos )
        self.vertX = list( self.vertices )
        
    def draw( self ):
        """ Render the point """
        # [1]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        if self.trnsByOGL:
            glTranslated( *self.pos3D ) # This moves the origin of drawing , so that we can use the above coordinates at each draw location
        # ( Rotation is not applicable to points )
        # [2]. Set color & size
        glColor3ub( *self.colors[0] ) 
        glPointSize( self.size )
        # [3]. Render! 
        # print "DEBUG ," , "self.vertX:  " , self.vertX 
        # print "DEBUG ," , "self.indices:" , self.indices
        pyglet.graphics.draw_indexed( 
            1 , # --------------------- Number of seqential triplet in vertex list
            GL_POINTS , # ------------- Draw quadrilaterals
            self.indices , # ----------------- Indices where the coordinates are stored
            ( 'v3f' , self.vertX ) # -- vertex list , OpenGL offers an optimized vertex list object , but this is not it
        )
        # [4]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        # ( Rotation is not applicable to points )
        if self.trnsByOGL:
            glTranslated( *np.multiply( self.pos3D , -1 ) ) # Reset the transform coordinates
        
# __ End Point __

# == class CartAxes ==

class CartAxes( OGLDrawable ):
    """ Standard set of Cartesian coordinate axes """
    # NOTE: At this time , will only draw the axes at the lab frame
    
    def __init__( self , origin = [ 0 , 0 , 0 ] , unitLen = 1.0 ):
        """ Set up the vertices for a coordinate axes """
        OGLDrawable.__init__( self , origin ) # ------------------------- Parent class init
        subLen = unitLen / 8.0 # Arrowhead 20% of the total length        
        
        self.vertices = ( # --------------------------------------------- Tuples of vertices that define the drawable geometry
                  0 ,       0 ,       0 ,     # 0 , Orgn
            unitLen ,       0 ,       0 ,     # 1 , X vec / arw
                  0 , unitLen ,       0 ,     # 2 , Y vec / arw
                  0 ,       0 , unitLen ,     # 3 , Z vec / arw
            unitLen - subLen ,  subLen , 0 ,  # 4 , X arw
            unitLen - subLen , -subLen , 0 ,  # 5 , X arw 
            0 , unitLen - subLen ,  subLen ,  # 6 , Y arw                   
            0 , unitLen - subLen , -subLen ,  # 7 , Y arw
             subLen , 0 , unitLen - subLen ,  # 8 , Z arw
            -subLen  , 0 , unitLen - subLen   # 9 , Z arw
        )
        
        self.vertX = list( self.vertices ) # ---------------------------- List of transformed vertices
        
        # These indices are used to draw the individual 
        # components of the coordinate axes
        self.ndx_Xvec = ( 0 , 1 ) ; self.ndx_Xarw = ( 1 , 4 , 5 ) # ----- Tuple of indices of 'vertX' that determine the which are 
        self.ndx_Yvec = ( 0 , 2 ) ; self.ndx_Yarw = ( 2 , 6 , 7 ) #       used to draw what parts of the geometry
        self.ndx_Zvec = ( 0 , 3 ) ; self.ndx_Zarw = ( 3 , 8 , 9 )
        self.vectors = ( self.ndx_Xvec , self.ndx_Yvec , self.ndx_Zvec )
        self.arrows  = ( self.ndx_Xarw , self.ndx_Yarw , self.ndx_Zarw )
        
        self.colors  = ( ( 255 ,   0 ,   0 ) ,  # ----------------------- All of the colors used to paint the object
                         (   0 , 255 ,   0 ) ,  # R = X , G = Y , B = Z
                         (   0 ,   0 , 255 )  ) # by convention
        
    def draw( self ):
        """ Draw the axes """
        # [1]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        self.state_transform()
        # [2]. Set color , size , and shape-specific parameters
        pyglet.gl.glLineWidth( 3 )
        # [3]. Render! # Basis vectors are drawn one at a time in the conventional colors
        for i in xrange(3): # 
            glColor3ub( *self.colors[i] )
            # Draw the arrow tail
            pyglet.graphics.draw_indexed( 
                10 , # ------------------ Number of seqential triplet in vertex list
                GL_LINES , # ------------ Draw quadrilaterals
                self.vectors[i] , # ----- Indices where the coordinates are stored
                ( 'v3f' , self.vertX ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
            )
            # Draw the arrow head
            pyglet.graphics.draw_indexed( 
                10 , # ------------------ Number of seqential triplet in vertex list
                GL_TRIANGLES , # -------- Draw quadrilaterals
                self.arrows[i] , # ------ Indices where the coordinates are stored
                ( 'v3f' , self.vertX ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
            )
        # [4]. If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        self.state_untransform()
            
# __ End CartAxes __


# == class Vector ==
        
class Vector_OGL( OGLDrawable ):
    """ A directed line segment """
    
    lineWidth  = 4 # - "LineWidth" # --------- Line width 
    arwLenFrac = 0.2 # "ArrowLengthFraction" # Fraction of the vector length that the arrowhead occupies
    arwWdtFrac = 0.1 # "ArrowWidthFraction" #- Fraction of the vector length that the arrowhead extends perpendicularly to the vector
    arwLngtLim = 0.5 # "ArrowLengthLimit" # -- Hard limit on arrowhead length in units -OR- Constant arrowhead length
    arwWdthLim = 0.5 # "ArrowWidthLimit" # --- Hard limit on arrowhead width in units  -OR- Constant arrowhead width
    
    @classmethod
    def set_vec_props( cls , **kwargs ):
        """ Set the visual properties of all the 'Vector_OGL' that will be subsequently created """
        if "LineWidth" in kwargs:
            cls.lineWidth  = kwargs["LineWidth"]
        if "ArrowLengthFraction" in kwargs:
            cls.arwLenFrac = kwargs["ArrowLengthFraction"]
        if "ArrowWidthFraction" in kwargs:
            cls.arwWdtFrac = kwargs["ArrowWidthFraction"]
        if "ArrowLengthLimit" in kwargs:
            cls.arwLngtLim = kwargs["ArrowLengthLimit"]
        if "ArrowWidthLimit" in kwargs:
            cls.arwWdthLim = kwargs["ArrowWidthLimit"]
    
    def set_origin_displace( self , origin , vec ):
        """ Set the vector so that it begins at 'origin' and has 'offset' """
        thisCls = self.__class__
        
        self.origin = origin
        self.offset = vec
        
        # print "DEBUG , origin _______________________________________ :" , origin
        # print "DEBUG , np.multiply( vec , ( 1 - thisCls.arwLenFrac ) ):" , np.multiply( vec , ( 1 - thisCls.arwLenFrac ) )
        
        drct80 = np.add( origin , np.multiply( vec , ( 1 - thisCls.arwLenFrac ) ) )
        
        if vec_mag( drct80 ) * thisCls.arwLenFrac > thisCls.arwLngtLim:
            drct80 = np.add( origin , np.multiply( vec , ( 1 - thisCls.arwLngtLim / vec_mag( drct80 ) ) ) )
        totalV = np.add( origin , vec )
        vecLen = vec_mag( vec )
        subLen = vecLen * thisCls.arwWdtFrac 
        hd1dir = vec_unit( np.cross( vec , [ 1 , 0 , 0 ] ) )
        hd2dir = vec_unit( np.cross( vec , hd1dir        ) )
        pointA = np.add( drct80 , np.multiply( hd1dir ,  subLen ) )
        pointB = np.add( drct80 , np.multiply( hd1dir , -subLen ) )
        pointC = np.add( drct80 , np.multiply( hd2dir ,  subLen ) )
        pointD = np.add( drct80 , np.multiply( hd2dir , -subLen ) )
        
        self.vertices = ( # --------------------------------------------- Tuples of vertices that define the drawable geometry
            origin[0] , origin[1] , origin[2] , # 0. Vector Tail
            totalV[0] , totalV[1] , totalV[2] , # 1. Vector Head
            pointA[0] , pointA[1] , pointA[2] , # 2. Fletching 1 Side 1
            pointB[0] , pointB[1] , pointB[2] , # 3. Fletching 1 Side 2
            pointC[0] , pointC[1] , pointC[2] , # 4. Fletching 2 Side 1
            pointD[0] , pointD[1] , pointD[2] , # 5. Fletching 2 Side 2
        )
        
        self.vertX = list( self.vertices ) # ---------------------------- List of transformed vertices
        
        self.ndx_vctr = ( 0 , 1 )
        self.ndx_flt1 = ( 1 , 2 , 3 )
        self.ndx_flt2 = ( 1 , 4 , 5 )
        self.fltchngs = [ self.ndx_flt1 , self.ndx_flt2 ]
    
    def __init__( self , origin = [ 0 , 0 , 0 ] , vec = [ 1 , 0 , 0 ] ):
        """ Set up the vertices for the vector """
        OGLDrawable.__init__( self , origin ) # ------------------------- Parent class init
        self.set_origin_displace( origin , vec )
        self.colors =  [ tuple( [  88 , 181 ,  74 ] ) ] # Body color
        
    def set_color( self , clrTpl ):
        """ Set the color of the vector """
        self.colors[0] = tuple( clrTpl )
        
    def draw( self ):
        """ Draw the axes """
        # [1]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        self.state_transform()
        # [2]. Set color , size , and shape-specific parameters
        pyglet.gl.glLineWidth( self.__class__.lineWidth )
        # [3]. Render! # Basis vectors are drawn one at a time in the conventional colors
        glColor3ub( *self.colors[0] ) # There is only one color
        # Draw the vector shaft
        pyglet.graphics.draw_indexed( 
            6 , # ------------------ Number of seqential triplet in vertex list
            GL_LINES , # ------------ Draw quadrilaterals
            self.ndx_vctr , # ----- Indices where the coordinates are stored
            ( 'v3f' , self.vertX ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
        )
        # Draw the fletchings
        for i in xrange( len( self.fltchngs ) ): 
            pyglet.graphics.draw_indexed( 
                6 , # ------------------ Number of seqential triplet in vertex list
                GL_TRIANGLES , # -------- Draw quadrilaterals
                self.fltchngs[i] , # ------ Indices where the coordinates are stored
                ( 'v3f' , self.vertX ) #- Vertex list , OpenGL offers an optimized vertex list object , but this is not it
            )
        # [4]. If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        self.state_untransform()
        
# __ End Vector __


# URL , Spatial Transforms: http://drake.mit.edu/doxygen_cxx/group__multibody__spatial__pose.html

# == class Cuboid ==

class Cuboid( OGLDrawable ):
    """ Rectangular prism rendered in Pyglet """
    
    def resize( self , l , w , h ):
        """ Assign the extents of the Cuboid in 'l'ength , 'w'idth , 'h'eight """
        self.l = l ; self.w = w ; self.h = h
        self.vertices = ( # ------------------ Tuple of vertices that define the drawable geometry
            0 , 0 , 0 ,	# vertex 0    3-------2     # NOTE: Z+ is UP
            l , 0 , 0 ,	# vertex 1    !\      !\
            0 , 0 , h ,	# vertex 2    ! \     Z \
            l , 0 , h ,	# vertex 3    !  7=======6
            0 , w , 0 ,	# vertex 4    1--|X---0  |
            l , w , 0 ,	# vertex 5     \ |     \ |
            0 , w , h ,	# vertex 6      \|      Y|
            l , w , h ,	# vertex 7       5=======4
        )
        self.vertX = list( self.vertices ) # List of transformed vertices
    
    def __init__( self , l , w , h , pos = [ 0 , 0 , 0 ] ):
        """ Create a rectangular prism with 'l' (x) , 'w' (y) , 'h' (z) """
        OGLDrawable.__init__( self , pos ) # -- Parent class init , Center will be used for OGL rendering transform
        # OGLDrawable.__init__( pos ) # -- Parent class init , Center will be used for OGL rendering transform
        
        self.resize( l , w , h ) # Assign the extents of the cuboid
        
        self.faceDices = ( #                                       NOTE: Vertices must have CCW order to point the normals towards exterior , 
             0 , 1 , 3 , 2 , # back face      3-----2    3-----2       right hand rule , otherwise dot products computed for backface-culling 
             4 , 6 , 7 , 5 , # front face     !\  up \   !back !\      will have the wrong sign! faces vanish!
             0 , 2 , 6 , 4 , # left face   right7=====6  !     ! 6
             1 , 5 , 7 , 3 , # right face     1 |front|  1-----0l|eft 
             0 , 4 , 5 , 1 , # down face       \|     |   \down \|
             2 , 3 , 7 , 6 , # up face          5=====4    5=====4          
        )
        
        self.linDices = (
            3 , 2 ,
            2 , 6 ,
            6 , 7 ,
            7 , 3 ,
            3 , 1 ,
            2 , 0 ,
            6 , 4 ,
            7 , 5 ,
            0 , 4 ,
            4 , 5 ,
            5 , 1 ,
            1 , 0
        )
        
        self.colors = ( (  88 , 181 ,  74 ) , # Body color
                        (   0 ,   0 , 255 ) ) # Line color
        
    def set_len( self , l ):
        """ Set the length of the Cuboid """
        self.resize( l , self.w , self.h )
        
    def draw( self ):
        """ Render the cuboid in OGL , This function assumes that a graphics context already exists """
        # [1]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        self.state_transform()
        # [2]. Set color , size , and shape-specific parameters
        glColor3ub( *self.colors[0] ) # Get the color according to the voxel type
        # [3]. Render! 
        pyglet.graphics.draw_indexed( 
            8 , # --------------------- Number of seqential triplet in vertex list
            GL_QUADS , # -------------- Draw quadrilaterals
            self.faceDices , # ---------- Indices where the coordinates are stored
            ( 'v3f' , self.vertX ) # vertex list , OpenGL offers an optimized vertex list object , but this is not it
        ) #   'v3i' # This is for integers I suppose!
        # [2]. Set color , size , and shape-specific parameters
        glColor3ub( *self.colors[1] ) # Get the color according to the voxel type
        pyglet.gl.glLineWidth( 3 )
        # [3]. Render! 
        pyglet.graphics.draw_indexed( 
            8 , # --------------------- Number of seqential triplet in vertex list
            GL_LINES , # -------------- Draw quadrilaterals
            self.linDices , # ---------- Indices where the coordinates are stored
            ( 'v3f' , self.vertX ) # vertex list , OpenGL offers an optimized vertex list object , but this is not it
        ) #   'v3i' # This is for integers I suppose!
        # [4]. If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        self.state_untransform()

# __ End Cuboid __
        
        
# == class Icosahedron ==

class Icosahedron_Reg( OGLDrawable ):
    """ Regular icosahedron rendered in Pyglet """
    
    def __init__( self , rad , pos = [ 0 , 0 , 0 ] ):
        """ Generate vertices from radius """
        # http://paulbourke.net/geometry/platonic/icosahedron.vf
        OGLDrawable.__init__( self , pos ) # -- Parent class init , Center will be used for OGL rendering transform
        self.sqrt5 = sqrt( 5.0 )
        self.phi = ( 1.0  + self.sqrt5 ) * 0.5 # "golden ratio"
        self.ratio = sqrt( 10.0 + ( 2.0  * self.sqrt5 ) ) / ( 4.0 * self.phi ) # ratio of edge length to radius
        a = self.a = ( rad / self.ratio ) * 0.5;
        b = self.b = ( rad / self.ratio ) / ( 2.0 * self.phi );
        
        self.vertices = (
             0 ,  b , -a ,
             b ,  a ,  0 ,
            -b ,  a ,  0 ,
             0 ,  b ,  a ,
             0 , -b ,  a ,
            -a ,  0 ,  b ,
             0 , -b , -a ,
             a ,  0 , -b ,
             a ,  0 ,  b ,
            -a ,  0 , -b ,
             b , -a ,  0 ,
            -b , -a ,  0 ,
        )
        self.vertX = list( self.vertices ) # List of transformed vertices
        
        self.faceDices = ( 
        #   CCW         ||  CW
            2 ,  1 ,  0 , #  v0    v1    v2
            1 ,  2 ,  3 , #  v3    v2    v1
            5 ,  4 ,  3 , #  v3    v4    v5
            4 ,  8 ,  3 , #  v3    v8    v4
            7 ,  6 ,  0 , #  v0    v6    v7
            6 ,  9 ,  0 , #  v0    v9    v6
           11 , 10 ,  4 , #  v4   v10   v11
           10 , 11 ,  6 , #  v6   v11   v10
            9 ,  5 ,  2 , #  v2    v5    v9
            5 ,  9 , 11 , # v11    v9    v5
            8 ,  7 ,  1 , #  v1    v7    v8
            7 ,  8 , 10 , # v10    v8    v7
            2 ,  5 ,  3 , #  v3    v5    v2
            8 ,  1 ,  3 , #  v3    v1    v8
            9 ,  2 ,  0 , #  v0    v2    v9
            1 ,  7 ,  0 , #  v0    v7    v1
           11 ,  9 ,  6 , #  v6    v9   v11
            7 , 10 ,  6 , #  v6   v10    v7
            5 , 11 ,  4 , #  v4   v11    v5
           10 ,  8 ,  4 , #  v4    v8   v10
        )
        
        self.colors = ( (  88 , 181 ,  74 ) , # Body color
                        (   0 ,   0 , 255 ) ) # Line color
        
        self.linDices = generate_segment_indices_for_OGmesh( self.faceDices )
        self.numPairs = len( self.linDices ) / 2
        print "DEBUG , There are" , len( self.linDices ) / 2 , "edges"
        
    def draw( self ):
        """ Render the Icosahedron in OGL , This function assumes that a graphics context already exists """
        # [1]. If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        self.state_transform()
        # [2]. Set color , size , and shape-specific parameters
        glColor3ub( *self.colors[0] ) # Get the color according to the voxel type
        # [3]. Render! 
        pyglet.graphics.draw_indexed( 
            12 , # --------------------- Number of seqential triplet in vertex list
            GL_TRIANGLES , # -------------- Draw quadrilaterals
            self.faceDices , # ---------- Indices where the coordinates are stored
            ( 'v3f' , self.vertX ) # vertex list , OpenGL offers an optimized vertex list object , but this is not it
        ) #   'v3i' # This is for integers I suppose!
        # [2]. Set color , size , and shape-specific parameters
        glColor3ub( *self.colors[1] ) # Get the color according to the voxel type
        pyglet.gl.glLineWidth( 3 )
        # [3]. Render! 
        pyglet.graphics.draw_indexed( 
            12 , # --------------------- Number of seqential triplet in vertex list
            GL_LINES , # -------------- Draw quadrilaterals
            self.linDices , # ---------- Indices where the coordinates are stored
            ( 'v3f' , self.vertX ) # vertex list , OpenGL offers an optimized vertex list object , but this is not it
        ) #   'v3i' # This is for integers I suppose!
        # [4]. If OGL transforms enabled , Return the OGL state machine to previous rendering frame
        self.state_untransform()
        

# __ End Icosahedron __

        
# == class NullDraw ==
        
class NullDraw( OGLDrawable ):
    """ An empty OGL object with dummy functions """
    
    def __init__( self , pnt = [ 0 , 0 , 0 ] ):
        """ Set up the parent functions """
        OGLDrawable.__init__( self , pnt ) # - Parent class init
        
    def add_vertex_offset( self , offset = [] ):
        """ Calc the relative positions of vertices given the center , Set a new offset if specified """
        pass
        
    def set_offset( self , offset ):
        """ Set center to that specified , Calc the relative positions of vertices given the center """
        pass
        
    def xform_homog( self , homogXform ):
        """ Transform all of the vertices with 'homogXform' (4x4) and store the result for rendering """
        pass
    
    def xform_Z_rot( self , thetaZrad ):
        """ Rotate all of the vertices in the list about the local Z axis """
        pass
        
    def xform_ang_axs( self , thetaRad , k ):
        """ Rotate all of the vertices in the list about the local Z axis """
        pass

    def state_transform( self ):
        """ Set the transformation matrix in the OGL state machine for this object """
        # If OGL transforms enabled , Translate and rotate the OGL state machine to desired rendering frame
        pass
            
    def state_untransform( self ):
        """ Unset the transformation matrix in the OGL state machine for this object , so that other shapes can set it for themselves """
        pass

    def draw( self ): 
        """ Render NOTHING """
        pass
    
        
# __ End NullDraw __
        
# ___ End Drawable ___


# == class OGL_App ==
        
class OGL_App( pyglet.window.Window ):
    """ Bookkeepping for Pyglet rendering """
    
    def __init__( self , objList = [] , caption = 'Pyglet Rendering Window' , dispWidth = 640 , dispHeight = 480 , 
                  clearColor = [ 0.7 , 0.7 , 0.8 , 1 ] ):
        """ Instantiate the environment with a list of objhects to render """
        super( OGL_App , self ).__init__( resizable = True , caption = caption ,  width = dispWidth , height = dispHeight )
        glClearColor( *clearColor ) # Set the BG color for the OGL window
        
        # URL: https://www.opengl.org/discussion_boards/showthread.php/165839-Use-gluLookAt-to-navigate-around-the-world
        self.camera = [  2 ,  2 ,  2 , # eyex    , eyey    , eyez    : Camera location , point (world) , XYZ
                         0 ,  0 ,  0 , # centerx , centery , centerz : Center of the camera focus , point (world) , XYZ
                         0 ,  0 ,  1 ] # upx     , upy     , upz     : Direction of "up" in the world frame , vector , XYZ
        
        self.renderlist = objList
        self.showFPS = False
        
    def set_camera( self , cameraLocationPnt , lookAtPoint , upDirection ):
        """ Specify the camera view """
        if ( len( cameraLocationPnt ) != 3 or len( lookAtPoint ) != 3 or len( upDirection ) != 3 ):
            raise IndexError( "OGL_App.set_camera: All parameters must be 3D vectors" )
        self.camera = concat_arr( cameraLocationPnt , # eyex    , eyey    , eyez    : Camera location , point (world) , XYZ
                                  lookAtPoint , #       centerx , centery , centerz : Center of the camera focus , point (world) , XYZ
                                  upDirection ) #       upx     , upy     , upz     : Direction of "up" in the world frame , vector , XYZ
        
    def setup_3D( self ):
        """ Setup the 3D matrix """
        # ~ Modes and Flags ~
        # Use 'GL_DEPTH_TEST' to ensure that OpenGL maintains a sensible drawing order for polygons no matter the viewing angle
        glEnable( GL_DEPTH_TEST ) # Do these setup functions really have to be run every single frame? # TODO: Try moving these to the '__init__' , see what happens
        # glEnable( GL_CULL_FACE ) # Uncomment to preform backface culling # This might erase arrowheads if they are away-facing!
        # ~ View Frustum Setup ~
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        gluPerspective( 70 , self.width / float( self.height ) , 0.1 , 200 ) # Camera properties
        # ~ View Direction Setup ~
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()
        gluLookAt( *self.camera )
            
    def on_draw( self ):
        """ Repaint the window , per-frame activity """
        self.clear()
        self.setup_3D()
        # print "DEBUG:" , "There are" , len( self.renderlist ) , "items in 'self.renderlist'"
        for obj in self.renderlist:
            obj.draw()
        if self.showFPS:
            print "FPS:" , pyglet.clock.get_fps() # Print the framerate

# __ End OGL_App __
            
# ____ End OpenGL ____
            
            
# === Spare Parts ==========================================================================================================================
            
""" 
URL: http://pyglet.readthedocs.io/en/pyglet-1.2-maintenance/programming_guide/graphics.html#vertex-lists
        
There is a significant overhead in using pyglet.graphics.draw and pyglet.graphics.draw_indexed due to pyglet 
interpreting and formatting the vertex data for the video device. Usually the data drawn in each frame (of an animation) 
is identical or very similar to the previous frame, so this overhead is unnecessarily repeated.

A VertexList is a list of vertices and their attributes, stored in an efficient manner that’s suitable for direct 
upload to the video card. On newer video cards (supporting OpenGL 1.5 or later) the data is actually stored in video memory.
"""
            
# ___ End Parts ____________________________________________________________________________________________________________________________
