########## INIT ###################################################################################
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt



########## Time Series ############################################################################


def plot_series_pretty( series_np , timeCol = -1 , labels = [] , linWght = 2 ,
                        title = "Plot" , xLbl = "X Axis" , yLbl = "Y Axis" , size = [ 12.0 , 7.0 ] ):
    """ Plot `series_np` where each column is one time-series """
    
    plt.figure( figsize = size )
    
    Ncols = series_np.shape[1]
    
    if timeCol >= 0:
        T = series_np[ : , timeCol ]
        # 1. For each of the series
        i = 1
        for srsDex in range( Ncols ):
            if srsDex != timeCol:
                
                if labels:
                    lbl = labels[ srsDex ]
                else:
                    lbl = str( i )
                    i += 1
                
                plt.plot( series_np[ : , timeCol ] , # Independent X
                          series_np[ : , srsDex  ] , # Dependent   Y
                          label = lbl , linewidth = linWght )  # FIXME , LINE WEIGHT, START HERE
            
    else:
        # 1. For each of the series
        for srsDex in range( Ncols ):
            if labels:
                lbl = labels[ srsDex ]
            else:
                lbl = str( srsDex+1 )
            plt.plot( series_np[ : , srsDex ] , label = lbl , linewidth = linWght )  # FIXME , LINE WEIGHT, START HERE
        
    
    plt.xlabel( xLbl )
    plt.ylabel( yLbl )
    plt.title( title )
    plt.legend( loc = 'best' )
    plt.show()## 