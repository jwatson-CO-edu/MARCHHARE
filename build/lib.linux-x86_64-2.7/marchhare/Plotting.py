#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2016-07-08

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
Plotting.py
James Watson, 2016 July
Useful functions for plotting, mostly in matplotlib
"""

# ~ Special Libraries ~
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D 

def split_to_components( vecList ):
    """ Separate a list of R3 vectors into three lists of components """ # because matplotlib likes it that way
    plotXs = []
    plotYs = []
    plotZs = []
    for vec in vecList:
        plotXs.append( vec[0] )
        plotYs.append( vec[1] )
        plotZs.append( vec[2] )
    return plotXs, plotYs, plotZs
    
def split_to_comp_cycle( vecList ):
    """ Separate a list of R3 vectors into three lists of components, in which the last item is a duplicate of the first """
    plotXs, plotYs, plotZs = split_to_components( vecList )
    plotXs.append( plotXs[0] )
    plotYs.append( plotYs[0] )
    plotZs.append( plotZs[0] )
    return plotXs, plotYs, plotZs
    
def split_to_2D( vecList ): 
    """ Separate a list of R2 vectors into two lists of components """ # because matplotlib likes it that way
    # NOTE: This will technically work for vectors of any dimensionaly 2 and above, indices > 1 will be ignored
    plotXs = []
    plotYs = []
    for vec in vecList:
        plotXs.append( vec[0] )
        plotYs.append( vec[1] )
    return plotXs, plotYs
    
def split_2d_on_XY_Zeq0( vecList ): 
    """ Separate a list of R2 vectors into three lists of components on the X-Y plane, Z = 0 """ 
    plotXs = []
    plotYs = []
    plotZs = []
    for vec in vecList:
        plotXs.append( vec[0] )
        plotYs.append( vec[1] )
        plotZs.append(      0 )
    return plotXs, plotYs, plotZs    
    
def plot_axes_3D_mpl(plotAX, scale = 1): 
    """ Display the coordinate axes in standard XYZ-RGB on a matplotlib 3D projection, each vector 'scale' in length """
    # NOTE: This function assumes that 'axes' has already been set up as a 3D projection subplot
    # URL, Show Origin: http://stackoverflow.com/a/11541628/893511
    # ax.plot( Xs    , Ys    , Zs    , c=COLORNAME )
    plotAX.plot( [0,scale] , [0,0    ] , [0,0    ] , c='r')
    plotAX.plot( [0,0    ] , [0,scale] , [0,0    ] , c='g')
    plotAX.plot( [0,0    ] , [0,0    ] , [0,scale] , c='b')
    
def plot_bases_3D_mpl( plotAX , origin , bX , bY , bZ , scale , labelNum = None ): 
    """ Display the supplied axes in standard XYZ-RGB on a matplotlib 3D projection, each vector 'scale' in length """
    # NOTE: This function assumes that 'axes' has already been set up as a 3D projection subplot
    # NOTE: This function does not perform any checks whatsoever on the orthogonality or length of bX, bY, bZ
    # URL, Show Origin: http://stackoverflow.com/a/11541628/893511
    # ax.plot( Xs    , Ys    , Zs    , c=COLORNAME )
    xVec = np.add( np.multiply( bX , scale ) , origin)
    yVec = np.add( np.multiply( bY , scale ) , origin)
    zVec = np.add( np.multiply( bZ , scale ) , origin)
    Xs, Ys, Zs = split_to_components( [ origin , xVec ] )
    plotAX.plot( Xs, Ys, Zs , c='r')
    Xs, Ys, Zs = split_to_components( [ origin , yVec ] )
    plotAX.plot( Xs, Ys, Zs , c='g')
    Xs, Ys, Zs = split_to_components( [ origin , zVec ] )
    plotAX.plot( Xs, Ys, Zs , c='b')
    if labelNum != None:
        xLoc = np.multiply( xVec , 1.1 )
        yLoc = np.multiply( yVec , 1.1 )
        zLoc = np.multiply( zVec , 1.1 )
        plotAX.text( xLoc[0] , xLoc[1] , xLoc[2] , "x_" + str(labelNum) , tuple(xVec) )
        plotAX.text( yLoc[0] , yLoc[1] , yLoc[2] , "y_" + str(labelNum) , tuple(yVec) )
        plotAX.text( zLoc[0] , zLoc[1] , zLoc[2] , "z_" + str(labelNum) , tuple(zVec) )
    
def plot_pose_axes_mpl( plotAX , vecPose , scale , labelNum = None ):
    """ Represent a Vector.Pose as 3D bases in a plot """
    plot_bases_3D_mpl(plotAX, 
                      vecPose.position, 
                      vecPose.orientation.apply_to( [ 1.0 , 0.0 , 0.0 ] ), 
                      vecPose.orientation.apply_to( [ 0.0 , 1.0 , 0.0 ] ), 
                      vecPose.orientation.apply_to( [ 0.0 , 0.0 , 1.0 ] ), 
                      scale,
                      labelNum)

def fig_num(): fig_num.num += 1 ; return fig_num.num # Functor to increment and return figure number with each call
fig_num.num = 0
 
def fig_3d():
    """ Create a new 3D figure and return handles to figure and axes """
    fig = plt.figure( fig_num() )
    ax = fig.add_subplot(111, projection='3d')
    return fig , ax
    
def show_3d():
    """ Show all the 3D figures, should only be called once per program """
    plt.gca().set_aspect('equal')
    plt.show()
   
def plot_points_only_list(ptsList):
    """ Plot the uniqueified points already stored in a list """ # NOTE: This function assumes a points-only file exists!
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    #pointsOnly = load_pkl_struct(PKLpath) # You must be aware of the structure in order to use it
    
    xs,ys,zs = split_to_components( ptsList )
    ax.scatter(xs, ys, zs, c='blue', marker='o', s=14)
    plot_axes_3D_mpl(ax, scale = 0.05)
    # Show the attachment point that will be used to attach to grasp points
    
    #xs,ys,zs = split_to_components( [indexFingTip] )
    #ax.scatter(xs, ys, zs, c='red', marker='+' , s=140)
    
    plt.gca().set_aspect('equal')
    plt.show()
    
def plot_chain(ptsList):
    """ Plot the uniqueified points already stored in a list """ # NOTE: This function assumes a points-only file exists!
    fig = plt.figure()
    #ax = Axes3D(fig) 
    ax = fig.add_subplot(111, projection='3d')
    #pointsOnly = load_pkl_struct(PKLpath) # You must be aware of the structure in order to use it
    
    xs,ys,zs = split_to_components( ptsList )
    ax.plot(xs, ys, zs, c='blue')
    plot_axes_3D_mpl(ax, scale = 0.05)
    # Show the attachment point that will be used to attach to grasp points
    
    #xs,ys,zs = split_to_components( [indexFingTip] )
    #ax.scatter(xs, ys, zs, c='red', marker='+' , s=140)
    
    plt.gca().set_aspect('equal')
    plt.show() 