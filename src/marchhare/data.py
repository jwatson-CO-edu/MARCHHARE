########## INIT ###################################################################################
import numpy as np


########## Data Retrieval #########################################################################


def json_from_file( path ):
    """ Parse JSON from the file at the given path and return the structured contents """
    with open( os.path.expanduser( path ) ) as f:
        data = json.load(f)
    return data


def load_CSV_for_NN( csvPath , elemParser = float ):
    """ Load a CSV file into a multidim array """
    rtnArr = []
    with open( csvPath , 'r' ) as fCSV:
        reader = csv.reader( fCSV )
        for row in reader:
            datum = [ elemParser( elem ) for elem in row ]
            rtnArr.append( datum )
    return np.array( rtnArr )



########## Data Processing ########################################################################
# NOTE: It does not make sense to normalize each column on its own because relative magnitudes between channels are NOT PRESERVED


def normalize_matrix( data_np, loBound = -1.0, hiBound = 1.0 ):
    """ Rescale `data_np` from [<global min>,<global max>] to [`loBound`,`hiBound`] """
    # 1. Get the greatest and least element in matrix
    hi = np.amax( data_np )
    lo = np.amin( data_np )
    # 2. Make same-size matrices of the limits
    hiArr = np.full( data_np.shape, hi      )
    loArr = np.full( data_np.shape, lo      )
    loBAr = np.full( data_np.shape, loBound )
    # 3. Scale the entire matrix and return
    #      (set min to zero) / (scale to [0,1])* (scale to [loB,hiB] ) + (start at loB)
    return (data_np - loArr) / (hiArr - loArr) * ( hiBound - loBound ) + loBAr


def normalize_rows_as_probs( data_np ):
    """ Normalize every row to sum to 1.0 """
    return scipy.special.softmax( data_np, axis = 1 )


def normalize_column_groups( data_np, groups, loBound = -1.0, hiBound = 1.0 ):
    """ Normalize individual groups of columns [..., [bgn,end], ...], For use in dataset with several channels of the same type """
    # 0. Copy the input matrix in case there are columns the user does not wish to normalize
    rtnArr = data_np.copy()
    # 1. For each group, run the matrix-wide normalization procedure
    for group in groups:
        # A. Get the group column index bounds
        gBgn = group[0]
        gEnd = group[1]
        # B. Fetch columns, normalize, and assign back to return matrix
        rtnArr[ : , gBgn:gEnd ] = normalize_matrix(  data_np[ : , gBgn:gEnd ], loBound, hiBound  )
    return rtnArr
    

def normalize_dataset_and_save( csvPath, npyPath, groups, loBound = -1.0, hiBound = 1.0 ):
    """ Load data from CSV, Noramlize it, then save it to NPY """
    # 1. Load the data
    data_NP = load_CSV_for_NN( csvPath , elemParser = float )
    # 2. Normalize data
    norm_NP = normalize_column_groups( data_NP, groups, loBound, hiBound )
    # 3. Save data
    np.save( npyPath, norm_NP, allow_pickle = 0 )


########## Time Series Interpolation ##############################################################


### Double Exp. Window Filter and Interpolate ###


def Holt_Winters_interpolate( data_np, alpha_dataFactor, beta_slopeFactor, ts = 20.0, timeCol = 0 ):
    """ Simultaneously apply Timestep-aware double exponential window and  """
    # https://en.wikipedia.org/wiki/Exponential_smoothing#Double_exponential_smoothing
    # https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc434.htm
    # https://www.nist.gov/nist-research-library/reference-format-nist-publications
    # NOTE: Returned array will have the same shape as the input array, see below
    
    # 0. Get dataset info
    tC     = timeCol # ---------- Column holding timestamps
    dRow   = data_np.shape[0] # ------- Number of datapoints in the 
    dCol   = data_np.shape[1] # ------- Number of channels
    lastTS = data_np[ -1, tC ] # ------ Last timestamp of the recording
    
    # 1. Split into timestamps and data
    Tx   = data_np[ : , tC    ].flatten()
    X    = data_np[ : , tC+1: ]
    xRow = X.shape[0]
    xCol = X.shape[1]
    
    # 2. Allocate and pre-populate the return series
    rRow = int( lastTS/ts )+1 # Number of `dt` timesteps that will fit in the recording == number of rows of returned data
    rCol = dCol
    R    = np.zeros( ( rRow, rCol ) )
    dtr  = ts
    R[0,:] = data_np[0,:]
    
    # Abbreviate eq. params
    A = alpha_dataFactor
    B = beta_slopeFactor
    
    # Raw X
    tx_i  = Tx[0]
    x_i   = X[0,:]
    dtx_i = Tx[1] - Tx[0]
    
    # Interpolated R
    j    = 0
    tr_j = 0.0
    sr_j = X[0,:]
    br_j = ( X[1,:] - X[0,:] ) / dtx_i
    
    
    # 3. For every row in the original data, Calculate the rolling exponential
    for i in range( 1, xRow ):
        
        # A. Stash X_{i-1} params
        tx_im1  = tx_i
        x_im1   = x_i
        dtx_im1 = dtx_i
        
        # A. Update X_{i} params
        tx_i  = Tx[i]
        x_i   = X[i,:]
        dtx_i = tx_i - tx_im1
        mx_i  = (x_i - x_im1)/dtx_i
        
        # Case 1: tr is behind tx, Update the R estimates and write rows
        while tr_j < tx_i:
            
            # 1. Stash R_{j-1} params
            tr_jm1 = tr_j
            sr_jm1 = sr_j
            br_jm1 = br_j
            
            # 2. Update R_{j} params
            j += 1
            tr_j = j*dtr
            
            # 3. Apply estimates of x_i until tx no longer applies
            # Smoothed data
            fctr = dtr/dtx_im1 if (dtr < dtx_im1) else dtx_im1/dtr
            sr_j = A*x_i + (1-A)*(sr_j + br_jm1*fctr) 
            # Smoothed slope
            fctr = dtr/dtx_i if (dtr < dtx_i) else dtx_i/dtr
            br_j = B*mx_i*fctr + (1-B)*br_jm1 
            
            # 4. Store the smoothed datapoint (if there is room)
            if j < rRow:
                R[ j, tC    ] = tr_j
                R[ j, tC+1: ] = sr_j
            
        # Case 2: tx is behind tr, Do nothing            

    # Make sure that last datapoint makes it in
    R[-1,:] = data_np[-1,:]
        
    # N. Return
    return R


########## Filtering ##############################################################################


def rolling_average( data_np, winSize = 5, ignoreFirstCols = 1 ):
    """ Return a version of the data with a rolling average of every column after the `ignoreFirstCols-1` column """  
    # NOTE: Returned array will have the same shape as the input array, see below
    
    # 0. Get shape info
    ( Nrows , Mcols ) = data_np.shape
    bgnC = int( ignoreFirstCols )
    endC = Mcols
    
    # 1. Pre-allocate array && init
    rtnArr = np.zeros( data_np.shape )
    rtnArr[ 0, : ] = data_np[ 0, : ]
    
    # 2. Compute rolling averages
    for i in range( 1, Nrows ):
        # 3. If there is not a full window, use what you got
        if i < (winSize-1):
            bgnR = 0
        else:
            bgnR = i-winSize+1
        endR = i+1
        
        # 4. Average for this row
        rtnArr[ i, bgnC:endC ] = np.mean( data_np[ bgnR:endR, bgnC:endC ], 0 )
        if ignoreFirstCols:
            rtnArr[ i, 0 ] = data_np[ i, 0 ]
        
    # N. Return
    return rtnArr



def Holt_Winters_double_exponential_window( data_np, alpha_dataFactor, beta_slopeFactor, ignoreFirstCols = 1 ):
    """ Apply the a version of the exponential window that has the capability to "follow trends" """
    # https://en.wikipedia.org/wiki/Exponential_smoothing#Double_exponential_smoothing
    # # https://www.nist.gov/nist-research-library/reference-format-nist-publications
    # NOTE: Returned array will have the same shape as the input array, see below
    # NOTE: USE THE NIST METHOD TO TUNE: https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc431.htm
    
    # 0. Get shape info
    ( Nrows , Mcols ) = data_np.shape
    bgnC = int( ignoreFirstCols )
    endC = Mcols
    
    # 1. Pre-allocate array
    rtnArr = np.zeros( data_np.shape )
    
    # 2. Init
    A   = alpha_dataFactor
    B   = beta_slopeFactor
    s_t = data_np[ 0, bgnC:endC ]
    b_t = data_np[ 1, bgnC:endC ] - data_np[ 0, bgnC:endC ]
    
    rtnArr[ 0, : ] = data_np[ 0, : ]
    
     # 2. Compute rolling exponential
    for i in range( 1, Nrows ):
        
        # A. Update the t-1 params
        s_tm1 = s_t
        b_tm1 = b_t
        
        # B. Compute new params
        s_t = A*data_np[ i, bgnC:endC ] + (1-A)*(s_tm1 + b_tm1) # Smoothed data
        b_t = B*(s_t - s_tm1) + (1-B)*b_tm1 # ------------------- Smoothed slope
        
        # C. Store the smoothed datapoint
        rtnArr[ i, bgnC:endC ] = s_t
        if ignoreFirstCols:
            rtnArr[ i, 0 ] = data_np[ i, 0 ]
        
    # N. Return
    return rtnArr


def Holt_Winters_dbbl_exp_ts( data_np, alpha_dataFactor, beta_slopeFactor, timeCol = 0 ):
    """ Timestep-aware double exponential window """
    # https://en.wikipedia.org/wiki/Exponential_smoothing#Double_exponential_smoothing
    # https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc434.htm
    # https://www.nist.gov/nist-research-library/reference-format-nist-publications
    # NOTE: Returned array will have the same shape as the input array, see below
    tC = timeCol
    dC = tC+1
    ( dRow, dCol ) = data_np.shape
    xRow = dRow
    xCol = dCol - dC
    
    # 0. Split into timestamps and data
    t = data_np[ : , tC  ].flatten()
    X = data_np[ : , dC: ]
    # 1. Allocate and pre-populate the return series
    R = np.zeros( ( dRow, dCol ) )
    R[:,tC] = t
    R[0,:]  = data_np[0,:]
    
    # 2. Init
    A   = alpha_dataFactor
    B   = beta_slopeFactor
    s_t = X[0,:]
    dt  = t[1] - t[0]
    b_t = ( X[1,:] - X[0,:] ) / dt
    t_i = t[0]
    
     # 2. Compute rolling exponential
    for i in range( 1, dRow ):
        
        # A. Update the t-1 params
        t_im1 = t_i
        s_tm1 = s_t
        b_tm1 = b_t
        dtm1  = dt
        
        # B. Compute new params
        t_i = t[i]
        dt  = t_i - t_im1
        # Smoothed data
        fctr = dt/dtm1 if (dt < dtm1) else dtm1/dt
        s_t  = A*X[i,:] + (1-A)*(s_tm1 + b_tm1*fctr) 
        # Smoothed slope
        m_t = (s_t - s_tm1)/dt
        b_t = B*m_t*fctr + (1-B)*b_tm1 
        
        # C. Store the smoothed datapoint
        R[ i, dC: ] = s_t
        
    # N. Return
    return R