import numpy as NP
import scipy.constants as FCNST
import lookup_operations as LKP

################################################################################

def parmscheck(xmax=1.0, ymax=1.0,rmin=0.0, rmax=1.0, rotangle=0.0,
               pointing_center=None):

    """
    ----------------------------------------------------------------------------
    Checks aperture parameters for compatibility for analytic aperture kernel 
    estimation

    xmax    [scalar] Upper limit along the x-axis for the aperture kernel 
            footprint. Applicable in case of rectangular or square apertures. 
            Default=1.0. Lower limit along the x-axis is set to -xmax. Length 
            of the rectangular footprint is 2*xmax

    ymax    [scalar] Upper limit along the y-axis for the aperture kernel 
            footprint. Applicable in case of rectangular apertures. 
            Default=1.0. Lower limit along the y-axis is set to -ymax. Breadth 
            of the rectangular footprint is 2*ymax

    rmin    [scalar] Lower limit along the radial direction for the aperture 
            kernel footprint. Applicable in case of circular apertures.  
            Default=0.0

    rmax    [scalar] Upper limit along the radial direction for the aperture 
            kernel footprint. Applicable in case of circular apertures.  
            Default=1.0

    rotangle
            [scalar] Angle (in radians) by which the principal axis of the 
            aperture is rotated counterclockwise east of sky frame. 
            Applicable in case of rectangular, square and elliptical 
            apertures. Default=0.0

    pointing_center
            [numpy array] Pointing center to phase the aperture illumination 
            to. Must be a 2-element array denoting the x- and y-direction 
            cosines that obeys rules of direction cosines. Default=None 
            (zenith)

    Outputs:

    Dictionary consisting of corrected values of input under the following 
    keys:
    'xmax'  [scalar] Corrected upper limit along the x-axis for the aperture 
            kernel footprint. Applicable in case of rectangular or square 
            apertures. 
    'ymax'  [scalar] Corrected upper limit along the y-axis for the aperture 
            kernel footprint. Applicable in case of rectangular
            apertures. 
    'rmin'  [scalar] Corrected lower limit along the radial direction for the 
            aperture kernel footprint. Applicable in case of circular apertures. 
            
    'rmax'  [scalar] Corrected upper limit along the radial direction for the 
            aperture kernel footprint. Applicable in case of circular apertures. 
            
    'rotangle'
            [scalar] Angle (in radians) by which the principal axis of the 
            aperture is rotated counterclockwise east of sky frame. 
    'pointing_center'
            [numpy array] Corrected pointing center to phase the aperture 
            illumination to. It is a 2-element array denoting the x- and 
            y-direction cosines
    ----------------------------------------------------------------------------
    """

    if not isinstance(xmax, (int,float)):
        raise TypeError('xmax must be a scalar')
    else:
        xmax = float(xmax)

    if not isinstance(ymax, (int,float)):
        raise TypeError('ymax must be a scalar')
    else:
        ymax = float(ymax)

    if xmax <= 0.0:
        raise ValueError('xmax must be positive')
    if ymax <= 0.0:
        raise ValueError('ymax must be positive')

    if not isinstance(rmin, (int,float)):
        raise TypeError('rmin must be a scalar')
    else:
        rmin = float(rmin)

    if not isinstance(rmax, (int,float)):
        raise TypeError('rmax must be a scalar')
    else:
        rmax = float(rmax)

    if rmin < 0.0:
        rmin = 0.0
    if rmin >= rmax:
        raise ValueError('rmin must be less than rmax')
    
    outdict = {}
    outdict['xmax'] = xmax
    outdict['ymax'] = ymax
    outdict['rmin'] = rmin
    outdict['rmax'] = rmax

    if not isinstance(rotangle, (int,float)):
        raise TypeError('Rotation angle must be a scalar')
    else:
        rotangle = float(rotangle)

    outdict['rotangle'] = rotangle
        
    if pointing_center is not None:
        if not isinstance(pointing_center, NP.ndarray):
            raise TypeError('pointing_center must be a numpy array')
        pointing_center = NP.squeeze(pointing_center)
        if pointing_center.size != 2:
            raise ValueError('pointing center must be a 2-element numpy array')
        if NP.sum(pointing_center**2) > 1.0:
            raise ValueError('pointing center incompatible with rules of direction cosines')
    else:
        pointing_center = NP.asarray([0.0, 0.0]).reshape(1,-1)

    outdict['pointing_center'] = pointing_center

    return outdict

################################################################################

def inputcheck(locs, wavelength=1.0, xmax=1.0, ymax=1.0, rmin=0.0, rmax=1.0,
               rotangle=0.0, pointing_center=None):

    """
    ----------------------------------------------------------------------------
    Checks inputs for compatibility for analytic aperture kernel estimation

    Inputs:

    locs    [numpy array] locations at which aperture kernel is to be estimated. 
            Must be a Mx2 numpy array where M is the number of locations, x- and 
            y-locations are stored in the first and second columns respectively.
            The units can be arbitrary but preferably that of distance. Must be
            specified, no defaults.

    wavelength
            [scalar or numpy array] Wavelength of the radiation. If it is a 
            scalar or numpy array of size 1, it is assumed to be identical for 
            all locations. If an array is provided, it must be of same size as
            the number of locations at which the aperture kernel is to be 
            estimated. Same units as locs. Default=1.0

    xmax    [scalar] Upper limit along the x-axis for the aperture kernel 
            footprint. Applicable in case of rectangular or square apertures. 
            Same units as locs. Default=1.0. Lower limit along the x-axis is 
            set to -xmax. Length of the rectangular footprint is 2*xmax

    ymax    [scalar] Upper limit along the y-axis for the aperture kernel 
            footprint. Applicable in case of rectangular apertures. 
            Same units as locs. Default=1.0. Lower limit along the y-axis is 
            set to -ymax. Breadth of the rectangular footprint is 2*ymax

    rmin    [scalar] Lower limit along the radial direction for the aperture 
            kernel footprint. Applicable in case of circular apertures. Same 
            units as locs. Default=0.0

    rmax    [scalar] Upper limit along the radial direction for the aperture 
            kernel footprint. Applicable in case of circular apertures. Same 
            units as locs. Default=1.0

    rotangle
            [scalar] Angle (in radians) by which the principal axis of the 
            aperture is rotated counterclockwise east of sky frame. 
            Applicable in case of rectangular, square and elliptical 
            apertures. Default=0.0

    pointing_center
            [numpy array] Pointing center to phase the aperture illumination 
            to. Must be a 2-element array denoting the x- and y-direction 
            cosines that obeys rules of direction cosines. Default=None 
            (zenith)

    Outputs:

    Dictionary consisting of corrected values of input under the following 
    keys:
    'locs'  [numpy array] Corrected locations for aperture kernel estimation. 
            Mx2 array for x and y coordinates of M locations. Same units as 
            locs
    'wavelength'
            [numpy array] Corrected wavelengths. 1x1 or Mx1 array. Same units
            as locs
    'xmax'  [scalar] Corrected upper limit along the x-axis for the aperture 
            kernel footprint. Applicable in case of rectangular or square 
            apertures. Same units as locs
    'ymax'  [scalar] Corrected upper limit along the y-axis for the aperture 
            kernel footprint. Applicable in case of rectangular
            apertures. Same units as locs
    'rmin'  [scalar] Corrected lower limit along the radial direction for the 
            aperture kernel footprint. Applicable in case of circular apertures. 
            Same units as locs
    'rmax'  [scalar] Corrected upper limit along the radial direction for the 
            aperture kernel footprint. Applicable in case of circular apertures. 
            Same units as locs
    'rotangle'
            [scalar] Angle (in radians) by which the principal axis of the 
            aperture is rotated counterclockwise east of sky frame. 
    'pointing_center'
            [numpy array] Corrected pointing center to phase the aperture 
            illumination to. It is a 2-element array denoting the x- and 
            y-direction cosines
    ----------------------------------------------------------------------------
    """

    try:
        locs
    except NameError:
        raise NameError('x and y locations must be specified in locs')

    if not isinstance(locs, NP.ndarray):
        raise TypeError('locs must be a numpy array')

    outdict = {}
    locs = NP.squeeze(locs)
    locs_shape = locs.shape
    locs_size = locs.size

    if (locs.ndim < 1) or (locs.ndim > 3):
        raise ValueError('locs must be a one-, two- or three-dimensional array')

    if locs.ndim == 1:
        if (locs_size < 2) or (locs_size > 3):
            raise ValueError('locs must contain at least two elements and not more than three elements')
        locs = locs[:2].reshape(1,-1)
    else:
        if locs.ndim == 3:
            locs = locs[:,:,0]
        if locs.shape[1] > 2:
            locs = locs[:,:2]

    outdict['locs'] = locs.reshape(-1,2)

    if not isinstance(wavelength, (int, float, NP.ndarray)):
        raise TypeError('wavelength must be a scalar or numpy array')
    else:
        wavelength = NP.asarray(wavelength, dtype=NP.float).reshape(-1)
        if (wavelength.size != 1) and (wavelength.size != locs.shape[0]):
            raise ValueError('Dimensions of wavelength are incompatible with those of locs')
        if NP.any(wavelength <= 0.0):
            raise ValueError('wavelength(s) must be positive')

    outdict['wavelength'] = wavelength
    
    parmsdict = parmscheck(xmax=xmax, ymax=ymax, rotangle=rotangle,
                           pointing_center=pointing_center)
    
    outdict['xmax'] = parmsdict['xmax']
    outdict['ymax'] = parmsdict['ymax']
    outdict['rmax'] = parmsdict['rmax']
    outdict['rotangle'] = parmsdict['rotangle']
    outdict['pointing_center'] = parmsdict['pointing_center']

    return outdict
        
################################################################################

def rect(locs, wavelength=1.0, xmax=1.0, ymax=1.0, rotangle=0.0,
         pointing_center=None):

    """
    ----------------------------------------------------------------------------
    Rectangular aperture kernel estimation

    Inputs:

    locs    [numpy array] locations at which aperture kernel is to be estimated. 
            Must be a Mx2 numpy array where M is the number of locations, x- and 
            y-locations are stored in the first and second columns respectively.
            The units can be arbitrary but preferably that of distance. Must be 
            specified, no defaults

    wavelength
            [scalar or numpy array] Wavelength of the radiation. If it is a 
            scalar or numpy array of size 1, it is assumed to be identical for 
            all locations. If an array is provided, number of wavelengths must 
            equal number of locations. Same units as locs. Default=1.0

    xmax    [scalar] Upper limit along the x-axis for the aperture kernel 
            footprint. Same units as locs. Default=1.0. Lower limit along the 
            x-axis is set to -xmax. Length of the rectangular footprint is 
            2*xmax

    ymax    [scalar] Upper limit along the y-axis for the aperture kernel 
            footprint. Same units as locs. Default=1.0. Lower limit along the 
            y-axis is set to -ymax. Length of the rectangular footprint is 
            2*ymax
    
    rotangle
            [scalar] Angle (in radians) by which the principal axis of the 
            aperture is rotated counterclockwise east of sky frame. 
            Default=0.0

    pointing_center
            [numpy array] Pointing center to phase the aperture illumination to.
            Must be a 2-element array denoting the x- and y-direction cosines
            that obeys rules of direction cosines. Default=None (zenith)

    Outputs:

    kern    [numpy array] complex aperture kernel with a value for each 
            location in the input. 
    ----------------------------------------------------------------------------
    """

    inpdict = inputcheck(locs, wavelength=wavelength, xmax=xmax, ymax=ymax,
                         rotangle=rotangle, pointing_center=pointing_center)
    locs = inpdict['locs']
    wavelength = inpdict['wavelength']
    xmax = inpdict['xmax']    
    ymax = inpdict['ymax']
    xmin = -xmax
    ymin = -ymax
    rotangle = inpdict['rotangle']
    pointing_center = inpdict['pointing_center']

    kern = NP.zeros(locs.shape[0], dtype=NP.complex64)
    if ymax > xmax:
        rotangle = rotangle + NP.pi/2

    # Rotate all locations by -rotangle to get x- and y-values relative to
    # aperture frame

    rotmat = NP.asarray([[NP.cos(-rotangle), -NP.sin(-rotangle)],
                         [NP.sin(-rotangle),  NP.cos(-rotangle)]])
    locs = NP.dot(locs, rotmat.T)

    ind = NP.logical_and((locs[:,0] >= xmin) & (locs[:,0] <= xmax), (locs[:,1] >= ymin) & (locs[:,1] <= ymax))
    kern[ind] = NP.exp(-1j * 2*NP.pi/wavelength[ind] * NP.dot(locs[ind,:], pointing_center.T).ravel())
    
    eps = 1e-10
    if NP.all(NP.abs(kern.imag) < eps):
        kern = kern.real

    return kern

################################################################################

def square(locs, wavelength=1.0, xmax=1.0, rotangle=0.0,
           pointing_center=None):

    """
    ----------------------------------------------------------------------------
    Square aperture kernel estimation

    Inputs:

    locs    [numpy array] locations at which aperture kernel is to be estimated. 
            Must be a Mx2 numpy array where M is the number of locations, x- and 
            y-locations are stored in the first and second columns respectively.
            The units can be arbitrary but preferably that of distance. Must be 
            specified, no defaults

    wavelength
            [scalar or numpy array] Wavelength of the radiation. If it is a 
            scalar or numpy array of size 1, it is assumed to be identical for 
            all locations. If an array is provided, number of wavelengths must 
            equal number of locations. Same units as locs. Default=1.0

    xmax    [scalar] Upper limit for the aperture kernel footprint. Same 
            units as locs. Default=1.0. Lower limit along the x-axis is set to 
            -xmax. Length of the square footprint is 2*xmax

    rotangle
            [scalar] Angle (in radians) by which the principal axis of the 
            aperture is rotated counterclockwise east of sky frame. 
            Default=0.0

    pointing_center
            [numpy array] Pointing center to phase the aperture illumination to.
            Must be a 2-element array denoting the x- and y-direction cosines
            that obeys rules of direction cosines. Default=None (zenith)

    Outputs:

    kern    [numpy array] complex aperture kernel with a value for each 
            location in the input. 
    ----------------------------------------------------------------------------
    """

    kern = rect(locs, wavelength=wavelength, xmax=xmax, ymax=xmax,
                rotangle=rotangle, pointing_center=pointing_center)

    return kern

################################################################################

def circular(locs, wavelength=1.0, rmin=0.0, rmax=1.0, pointing_center=None):

    """
    ----------------------------------------------------------------------------
    Uniform circular aperture kernel estimation

    Inputs:

    locs    [numpy array] locations at which aperture kernel is to be estimated. 
            Must be a Mx2 numpy array where M is the number of locations, x- and 
            y-locations are stored in the first and second columns respectively.
            The units can be arbitrary but preferably that of distance. Must be
            specified, no defaults.

    wavelength
            [scalar or numpy array] Wavelength of the radiation. If it is a 
            scalar or numpy array of size 1, it is assumed to be identical for 
            all locations. If an array is provided, number of wavelengths must 
            equal number of locations. Same units as locs. Default=1.0

    rmin    [scalar] Lower limit along the radial direction for the aperture 
            kernel footprint. Applicable in case of circular apertures. Same 
            units as locs. Default=0.0

    rmax    [scalar] Upper limit along the radial direction for the aperture 
            kernel footprint. Applicable in case of circular apertures. Same 
            units as locs. Default=1.0

    pointing_center
            [numpy array] Pointing center to phase the aperture illumination 
            to. Must be a 2-element array denoting the x- and y-direction 
            cosines that obeys rules of direction cosines. Default=None 
            (zenith)

    Outputs:

    kern    [numpy array] complex aperture kernel with a value for each 
            location in the input. 
    ----------------------------------------------------------------------------
    """
    
    inpdict = inputcheck(locs, wavelength=wavelength, rmin=rmin, rmax=rmax,
                         pointing_center=pointing_center)
    locs = inpdict['locs']
    wavelength = inpdict['wavelength']
    rmin = inpdict['rmin']
    rmax = inpdict['rmax']
    pointing_center = inpdict['pointing_center']

    kern = NP.zeros(locs.shape[0], dtype=NP.complex64)

    radii = NP.sqrt(NP.sum(locs**2, axis=1))
    ind = (radii >= rmin) & (radii <= rmax) 
    kern[ind] = NP.exp(-1j * 2*NP.pi/wavelength[ind] * NP.dot(locs[ind,:], pointing_center.T).ravel())
    
    eps = 1e-10
    if NP.all(NP.abs(kern.imag) < eps):
        kern = kern.real

    return kern
    
################################################################################

class AntennaAperture(object):

    """
    ----------------------------------------------------------------------------
    Class to manage collective information on a group of antennas.

    Attributes:

    kernel_type [dictionary] denotes whether the kernel is analytic or based on
                a lookup table. It has two keys 'P1' and 'P2' - one for each 
                polarization. Under each key the allowed values are 'func' and
                'lookup' (default). If specified as None during initialization,
                it is set to 'lookup' under both polarizations.

    shape       [dictionary] denotes the shape of the aperture. It has two keys 
                'P1' and 'P2' - one for each polarization. Under each key the 
                allowed values are under each polarization are 'rect', 'square',
                'circular' or None. These apply only if the corresponding 
                kernel_type for the polarization is set to 'func' else the 
                shape will be set to None.

    xmax        [dictionary] Upper limit along the x-axis for the aperture 
                kernel footprint. Applicable in case of rectangular or square 
                apertures. It has two keys 'P1' and 'P2' - one for each 
                polarization. The value (default=1.0) held by each key is a 
                scalar. Lower limit along the x-axis is set to -xmax. Length 
                of the rectangular/square footprint is 2*xmax

    ymax        [dictionary] Upper limit along the y-axis for the aperture 
                kernel footprint. Applicable in case of rectangular 
                apertures. It has two keys 'P1' and 'P2' - one for each 
                polarization. The value (default=1.0) held by each key is a 
                scalar. Lower limit along the y-axis is set to -ymax. Breadth 
                of the rectangular footprint is 2*ymax

    rmin        [dictionary] Lower limit along the radial axis for the aperture 
                kernel footprint. Applicable in case of circular 
                apertures. It has two keys 'P1' and 'P2' - one for each 
                polarization. The value (default=0.0) held by each key is a 
                scalar

    rmax        [dictionary] Upper limit along the radial axis for the aperture 
                kernel footprint. Applicable in case of circular
                apertures. It has two keys 'P1' and 'P2' - one for each 
                polarization. The value (default=1.0) held by each key is a 
                scalar

    rotangle    [dictionary] Angle (in radians) by which the principal axis of the 
                aperture is rotated counterclockwise east of sky frame. 
                Applicable in case of rectangular, square and elliptical 
                apertures. It has two keys 'P1' and 'P2' - one for each 
                polarization. The value (default=0.0) held by each key is a 
                scalar

    lkpinfo     [dictionary] lookup table file location, one for each 
                polarization under the standard keys denoting polarization

    wtsposxy    [dictionary] two-dimensional locations of the gridding weights 
                in wts for each polarization under keys 'P1' and 'P2'. The 
                locations are in ENU coordinate system as a list of 2-column 
                numpy arrays in units of distance. 

    wtsxy       [dictionary] The gridding weights for antenna. Different 
                polarizations 'P1' and 'P2' form the keys of this dictionary. 
                These values are in general complex. Under each key, the values 
                are maintained as a numpy array of complex antenna weights 
                corresponding to positions in the lookup table. It should be of 
                same size as the number of rows in wtsposxy
    
    Member functions:

    __init__()  Initializes an instance of class AntennaAperture which manages
                information about an antenna aperture

    compute()   Estimates the kernel for given locations based on the aperture 
                attributes

    Read the member function docstrings for details.
    ----------------------------------------------------------------------------
    """

    def __init__(self, kernel_type=None, shape=None, parms=None, lkpinfo=None,
                 load_lookup=True):

        """
        ------------------------------------------------------------------------
        Initializes an instance of class AntennaAperture which manages
        information about an antenna aperture

        Class attributes initialized are:
        kernel_type, shape, xmax, ymax, rmin, emax, rotangle, 
        wtsposxy, wtsxy, lkpinfo

        Read docstring of class AntennaAperture for details on these 
        attributes.

        Inputs:

        kernel_type [dictionary] denotes whether the kernel is analytic or based 
                    on a lookup table. It has two keys 'P1' and 'P2' - one for 
                    each polarization. Under each key the allowed values are 
                    'func' and 'lookup' (default). If specified as None,
                    it is set to 'lookup' under both polarizations.
    
        shape       [dictionary] denotes the shape of the aperture. It has two 
                    keys 'P1' and 'P2' - one for each polarization. Under each 
                    key the allowed values are under each polarization are 
                    'rect', 'square', 'circular' or None. These apply only if 
                    the corresponding kernel_type for the polarization is set 
                    to 'func' else the shape will be set to None.

        parms       [dictionary] denotes parameters of the aperture shape. It 
                    has two keys 'P1' and 'P2' - one for each polarization. 
                    Under each of these keys is another dictionary with the 
                    following keys and information:
                    'xmax'  [scalar] Upper limit along the x-axis for the 
                            aperture kernel footprint. Applicable in case of 
                            rectangular or square apertures. Default=1.0.
                            Lower limit along the x-axis is set to -xmax. 
                            Length of the rectangular/square footprint is 
                            2*xmax
                    'ymax'  [scalar] Upper limit along the y-axis for the 
                            aperture kernel footprint. Applicable in case of 
                            rectangular apertures. Default=1.0. Lower limit 
                            along the y-axis is set to -ymax. Breadth of the 
                            rectangular footprint is 2*ymax
                    'rmin'  [scalar] Lower limit along radial axis for the 
                            aperture kernel footprint. Applicable in case of 
                            circualr apertures. Default=0.0
                    'rmax'  [scalar] Upper limit along radial axis for the 
                            aperture kernel footprint. Applicable in case of 
                            circular apertures. Default=1.0
                    'rotangle'
                            [scalar] Angle (in radians) by which the principal 
                            axis of the aperture is rotated counterclockwise 
                            east of sky frame. Applicable in case of 
                            rectangular, square and elliptical apertures. It 
                            has two keys 'P1' and 'P2' - one for each 
                            polarization. The value (default=0.0) held by each 
                            key is a scalar

        lkpinfo     [dicitonary] consists of weights information for each of 
                    the two polarizations under keys 'P1' and 'P2'. Each of 
                    the values under the keys is a string containing the full
                    path to a filename that contains the positions and 
                    weights for the antenna field illumination in the form of 
                    a lookup table as columns (x-loc [float], y-loc 
                    [float], wts[real], wts[imag if any]). 

        load_lookup [boolean] If set to True (default), loads from the lookup 
                    table. If set to False, the values may be loaded later 
                    using member function compute()
        ------------------------------------------------------------------------
        """

        if kernel_type is None:
            kernel_type = {}
            for pol in ['P1','P2']:
                kernel_type[pol] = 'lookup'
        elif isinstance(kernel_type, dict):
            for pol in ['P1','P2']:
                if pol not in kernel_type:
                    kernel_type[pol] = 'lookup'
                elif kernel_type[pol] not in ['lookup', 'func']:
                    raise ValueError('Invalid value specified for kernel_type under polarization {0}'.format(pol))
        else:
            raise TypeError('kernel_type must be a dictionary')

        if shape is None:
            shape = {}
            for pol in ['P1','P2']:
                if kernel_type[pol] == 'lookup':
                    shape[pol] = None
                else:
                    shape[pol] = 'circular'
        elif isinstance(shape, dict):
             for pol in ['P1','P2']:
                if pol not in shape:
                    if kernel_type[pol] == 'lookup':
                        shape[pol] = None
                    else:
                        shape[pol] = 'circular'
                else:
                    if kernel_type[pol] != 'func':
                        raise ValueError('Values specified in kernel_type and shape are incompatible')
                    elif shape[pol] not in ['rect', 'square', 'circular']:
                        raise ValueError('Invalid value specified for shape under polarization {0}'.format(pol))
        else:
            raise TypeError('Aperture kernel shape must be a dictionary')
            
        if parms is None:
            parms = {}
            for pol in ['P1','P2']:
                parms[pol] = {}
                parms[pol]['rmin'] = 0.0
                parms[pol]['xmax'] = 1.0
                parms[pol]['ymax'] = 1.0
                parms[pol]['rmax'] = 1.0
                parms[pol]['rotangle'] = 0.0
        elif isinstance(parms, dict):
            for pol in ['P1','P2']:
                if pol not in parms:
                    parms[pol] = {}
                    parms[pol]['rmin'] = 0.0
                    parms[pol]['xmax'] = 1.0
                    parms[pol]['ymax'] = 1.0
                    parms[pol]['rmax'] = 1.0
                    parms[pol]['rotangle'] = 0.0
                elif isinstance(parms[pol], dict):
                    if 'rmin' not in parms[pol]: parms[pol]['rmin'] = 0.0
                    if 'xmax' not in parms[pol]: parms[pol]['xmax'] = 1.0
                    if 'ymax' not in parms[pol]: parms[pol]['ymax'] = 1.0
                    if 'rmax' not in parms[pol]: parms[pol]['rmax'] = 1.0
                    if 'rotangle' not in parms[pol]: parms[pol]['rotangle'] = 0.0
                else:
                    raise TypeError('Aperture parameters under polarization {0} must be a dictionary'.format(pol))
        else:
            raise TypeError('Aperture kernel parameters must be a dictionary')

        self.kernel_type = {}
        self.shape = {}
        self.rmin = {}
        self.xmax = {}
        self.ymax = {}
        self.rmax = {}
        self.rotangle = {}
            
        for pol in ['P1', 'P2']:
            self.kernel_type[pol] = kernel_type[pol]
            self.shape[pol] = shape[pol]
            parmsdict = parmscheck(xmax=parms[pol]['xmax'], ymax=parms[pol]['ymax'], rmin=parms[pol]['rmin'], rmax=parms[pol]['rmax'], rotangle=parms[pol]['rotangle'])
            self.rmin[pol] = parmsdict['rmin']
            self.xmax[pol] = parmsdict['xmax']
            self.ymax[pol] = parmsdict['ymax']
            self.rmax[pol] = parmsdict['rmax']
            self.rotangle[pol] = parmsdict['rotangle']

        self.wtsposxy = {}
        self.wtsxy = {}
        self.lkpinfo = {}
        if lkpinfo is not None:
            if not isinstance(lkpinfo, dict):
                raise TypeError('Input parameter lkpinfo must be a dictionary')
            for pol in ['P1', 'P2']:
                self.wtsposxy[pol] = None
                self.wtsxy[pol] = None
                if pol in lkpinfo:
                    self.lkpinfo[pol] = lkpinfo[pol]
                    if load_lookup:
                        lkpdata = LKP.read_lookup(self.lkpinfo[pol])
                        self.wtsposxy[pol] = NP.hstack((lkpdata[0].reshape(-1,1),lkpdata[1].reshape(-1,1)))
                        self.wtsxy[pol] = lkpdata[2]
                        if len(lkpdata) == 4:  # Read in the imaginary part
                            self.wtsxy[pol] += 1j * lkpdata[3]

    ############################################################################

    def compute(self, locs, wavelength=1.0, pointing_center=None, pol=None,
                rmaxNN=None, load_lookup=False):

        """
        ------------------------------------------------------------------------
        Estimates the kernel for given locations based on the aperture 
        attributes for an analytic or lookup-based estimation

        Inputs:

        locs    [numpy array] locations at which aperture kernel is to be 
                estimated. Must be a Mx2 numpy array where M is the number of 
                locations, x- and y-locations are stored in the first and second 
                columns respectively. The units can be arbitrary but preferably 
                that of distance. Must be specified, no defaults.

        wavelength
                [scalar or numpy array] Wavelength of the radiation. If it is a 
                scalar or numpy array of size 1, it is assumed to be identical 
                for all locations. If an array is provided, it must be of same 
                size as the number of locations at which the aperture kernel is 
                to be estimated. Same units as locs. Default=1.0

        pointing_center
                [numpy array] Pointing center to phase the aperture illumination 
                to. Must be a 2-element array denoting the x- and y-direction 
                cosines that obeys rules of direction cosines. Default=None 
                (zenith)

        pol     [string or list] The polarization for which the kernel is to be 
                estimated. Can be set to 'P1' or 'P2' or  list containing both. 
                If set to None, kernel is estimated for all the polarizations. 
                Default=None

        rmaxNN  [scalar] Search distance upper limit in case of kernel 
                estimation from a lookup table. Default=None means value in 
                attribute rmax is used.

        load_lookup
                [boolean] If set to True, loads from the lookup table. If set
                to False (default), uses the already loaded values during 
                initialization

        Outputs:

        Dictionary containing two keys 'P1' and 'P2' - one for each 
        polarization. Under each of these keys, the kernel information is 
        returned as a (complex) numpy array
        ------------------------------------------------------------------------
        """

        if pol is None:
            pol = ['P1', 'P2']
        elif not isinstance(pol, list):
            if pol not in ['P1', 'P2']:
                raise ValueError('Invalid value specified for pol')
            pol = [pol]
        else:
            pol = set(pol)
            p = [item for item in pol if item in ['P1', 'P2']]
            pol = p

        outdict = {}
        for p in pol:
            outdict[p] = None
            if self.kernel_type[p] == 'func':
                if self.shape[p] is not None:
                    if self.shape[p] == 'rect':
                        outdict[p] = rect(locs, wavelength=wavelength, xmax=self.xmax[p], ymax=self.ymax[p], rotangle=self.rotangle[p], pointing_center=pointing_center)
                    elif self.shape[p] == 'square':
                        outdict[p] = square(locs, wavelength=wavelength, xmax=self.xmax[p], rotangle=self.rotangle[p], pointing_center=pointing_center)
                    elif self.shape[p] == 'circular':
                        outdict[p] = circular(locs, wavelength=wavelength, rmin=self.rmin[p], rmax=self.rmax[p], pointing_center=pointing_center)
                    else:
                        raise ValueError('The analytic kernel shape specified in the shape attribute is not currently supported')
            else:
                if rmaxNN is None:
                    rmaxNN = self.rmax
                if not isinstance(rmaxNN, (int,float)):
                    raise TypeError('Input rmaxNN must be a scalar')
                else:
                    rmaxNN = float(rmaxNN)
                    if rmaxNN <= 0.0:
                        raise ValueError('Search radius upper limit must be positive')

                if p in self.lkpinfo:
                    if load_lookup:
                        lkpdata = LKP.read_lookup(self.lkpinfo[p])
                        self.wtsposxy[p] = NP.hstack((lkpdata[0].reshape(-1,1),lkpdata[1].reshape(-1,1)))
                        self.wtsxy[p] = lkpdata[2]
                        if len(lkpdata) == 4:  # Read in the imaginary part
                            self.wtsxy[p] += 1j * lkpdata[3]

                    # inpind, refind, distNN = LKP.find_1NN(self.wtsposxy[p], locs, distance_ULIM=rmaxNN, remove_oob=True)
                    inpind, nnval, distNN = LKP.lookup_1NN_new(self.wtsposxy[p], self.wtsxy[p], locs, distance_ULIM=rmaxNN, remove_oob=False)
                    outdict[p] = nnval

        return outdict
            
    ############################################################################

        
        
            
        
            
        
