import datetime as DT
import numpy as NP
import matplotlib.pyplot as PLT
import matplotlib.colors as PLTC
import scipy.constants as FCNST
import antenna_array as AA
import geometry as GEOM
import sim_observe as SIM
import my_DSP_modules as DSP
import ipdb as PDB
import MOFF_cal

cal_iter=1
itr = 20*cal_iter

# Antenna initialization

lat = -26.701 # Latitude of MWA in degrees
f0 = 150e6 # Center frequency

antenna_file = '/data3/t_nithyanandan/project_MWA/MWA_128T_antenna_locations_MNRAS_2012_Beardsley_et_al.txt'
ant_info = NP.loadtxt(antenna_file, skiprows=6, comments='#', usecols=(0,1,2,3))
ant_info[:,1] -= NP.mean(ant_info[:,1])
ant_info[:,2] -= NP.mean(ant_info[:,2])
#ant_info[:,3] -= NP.mean(ant_info[:,3])
ant_info[:,3] = 0.0

core_ind = NP.logical_and((NP.abs(ant_info[:,1]) < 150.0), (NP.abs(ant_info[:,2]) < 150.0))
ant_info = ant_info[core_ind,:]

n_antennas = ant_info.shape[0]
    
nchan = 4
f_center = f0
channel_width = 40e3
bandwidth = nchan * channel_width
dt = 1/bandwidth

# use a single point source off center
n_src = 1
skypos = np.array([[0.010929/2,0.0]]) # note that this gets switched in the images.
src_flux = np.ones(n_src)

nvect = np.sqrt(1.0-np.sum(skypos**2, axis=1)).reshape(-1,1) # what is this?
skypos = np.hstack((skypos,nvect))

# set up antenna array
ants = []
for i in xrange(n_antennas):
    ants += [AA.Antenna('A'+'{0:d}'.format(int(ant_info[i,0])),lat,ant_info[i,1:],f0)]

# build antenna array
aar = AA.AntennaArray()
for ant in ants:
    aar = aar + ant

antpos_info = aar.antenna_positions(sort=True)

# set up calibration
calarr={}
sky_model=NP.zeros((3,n_src,nchan))
for i in xrange(n_src):
    sky_model[2,i,:]=src_flux[i]
    sky_model[0,i,:]=skypos[i,0]
    sky_model[1,i,:]=skypos[i,1]
ant_info[:,1:] = ant_info[:,1:] / FCNST.c * f0
    
for pol in ['P1','P2']:
    calarr[pol]=MOFF_cal.cal(ant_info.shape[0],nchan,n_iter=cal_iter,sim_mode=True,sky_model=sky_model,gain_factor=0.65,inv_gains=False,cal_method='off_center')
    #calarr[pol].scramble_gains(0.5) 
ncal=itr/cal_iter
cali=0
# Create array of gains to watch them change
gain_stack = NP.zeros((ncal+1,ant_info.shape[0],nchan),dtype=NP.complex64)
amp_stack = NP.zeros((ncal+1,nchan),dtype=NP.float64)
amp_full_stack = NP.zeros((itr,nchan),dtype=NP.float64)
temp_amp = NP.zeros(nchan,dtype=NP.float64)

for i in xrange(itr):
    print i
    # simulate
    E_timeseries_dict = SIM.stochastic_E_timeseries(f_center, nchan/2, 2*channel_width,
                                                    flux_ref=src_flux, skypos=skypos, antpos=antpos_info['positions'],tshift=False)

    timestamp = str(DT.datetime.now())
    update_info={}
    update_info['antennas']=[]
    update_info['antenna_array']={}
    update_info['antenna_array']['timestamp']=timestamp
    for label in aar.antennas:
        adict={}
        adict['label']=label
        adict['action']='modify'
        adict['timestamp']=timestamp
        ind = antpos_info['labels'].index(label)
        adict['t'] = E_timeseries_dict['t']
        adict['gridfunc_freq'] = 'scale'
        adict['gridmethod'] = 'NN'
        adict['distNN'] = 3.0
        adict['Et'] = {}
        adict['flags'] = {}
        adict['wtsinfo'] = {}
        for pol in ['P1','P2']:
            adict['flags'][pol] = False
            adict['Et'][pol] = E_timeseries_dict['Et'][:,ind]
            adict['wtsinfo'][pol] = [{'orientation':0.0, 'lookup':'/data3/t_nithyanandan/project_MOFF/simulated/LWA/data/lookup/E_illumination_isotropic_radiators_lookup_zenith.txt'}]

        update_info['antennas'] += [adict]

    aar.update(update_info, parallel=True, verbose=False, nproc=16)
    
    ### Calibration steps
    # read in data array
    aar.caldata['P1']=aar.get_E_fields('P1',sort=True)
    tempdata=aar.caldata['P1']['E-fields'][0,:,:].copy()
    #tempdata[:,2]=tempdata[:,2]/NP.abs(tempdata[0,2]) # uncomment this line to make noise = 0
    #tempdata[:,:]=1.0
    tempdata = calarr['P1'].apply_cal(tempdata,meas=True)
    amp_full_stack[i,:] = NP.abs(tempdata[0,:])**2
    # Apply calibration and put back into antenna array
    aar.caldata['P1']['E-fields'][0,:,:]=calarr['P1'].apply_cal(tempdata)

    aar.grid_convolve(pol='P1', method='NN',distNN=0.5*FCNST.c/f0, tol=1.0e-6,maxmatch=1,identical_antennas=True,gridfunc_freq='scale',mapping='weighted',wts_change=False,parallel=False,pp_method='queue', nproc=16, cal_loop=True,verbose=False)

    imgobj = AA.NewImage(antenna_array=aar, pol='P1')
    imgobj.imagr(weighting='natural',pol='P1',pad='off',verbose=False)

    # update calibration
    yind = NP.where(NP.abs(imgobj.gridl[0,:]-skypos[0][0])==NP.min(NP.abs(imgobj.gridl[0,:]-skypos[0][0])))
    xind = NP.where(NP.abs(imgobj.gridm[:,0]-skypos[0][1])==NP.min(NP.abs(imgobj.gridm[:,0]-skypos[0][1])))
    imgdata = imgobj.holimg['P1'][xind,yind,:]
    imgdata = imgdata.flatten()
    # TODO: Add frequency dependence of antenna locations! 
    calarr['P1'].update_cal(tempdata,imgdata,calarr['P1'].sky_model,antpos_info['positions'] / FCNST.c * f0)
    
    if i == 0:
        avg_img = NP.abs(imgobj.img['P1'])**2 - NP.nanmean(NP.abs(imgobj.img['P1'])**2)
        im_stack = NP.zeros((ncal,avg_img.shape[0],avg_img.shape[1]),dtype=NP.double)
        im_stack[cali,:,:] = avg_img[:,:,0]
        temp_im = avg_img[:,:,0]
    
        temp_amp = NP.abs(tempdata[0,:])**2
        gain_stack[cali,:,:] = calarr['P1'].sim_gains
        amp_stack[cali,:] = NP.abs(tempdata[0,:])**2
        cali += 1
        gain_stack[cali,:,:] = calarr['P1'].curr_gains
    
    else:
        avg_img += imgobj.img['P1']
        temp_im += imgobj.img['P1'][:,:,0]
      
        temp_amp += NP.abs(tempdata[0,:])**2
        if i % cal_iter == 0:
            im_stack[cali,:,:] = temp_im/cal_iter
            temp_im[:] = 0.0
            gain_stack[cali,:,:] = calarr['P1'].curr_gains
            amp_stack[cali,:] = temp_amp/cal_iter
            temp_amp[:] = 0.0
            cali += 1



    if True in NP.isnan(calarr['P1'].temp_gains):
        print 'NAN in calibration gains! exiting!'
        break

avg_img /= itr





