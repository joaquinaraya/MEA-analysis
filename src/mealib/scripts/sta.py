import h5py
import numpy as np
import matplotlib.pyplot as plt

from mealib.analysis import sta

SAVA_FILE = False

intensity = '32'
exp_name = 'MR-0181_intensity'+intensity
source_folder = '/home/cesar/exp/MEA-analysis/data/'
stim_file = source_folder+'stim/checkerboard/stim_mini_MR-0181_'+intensity+'_.hdf5'
sorting_file = source_folder+'sorting/MR-0181/MR-0181.result.hdf5'
sync_file = source_folder+'sync/MR-0181/event_list/244.txt'

# Parameters
nsamples_before=30
nsamples_after=0
fps = 59.75789
step = (np.arange(-nsamples_before, nsamples_after)+1)/fps

# Sync
sync_times = np.loadtxt(sync_file).T
start_frame = sync_times[0]
end_frame = sync_times[1]
start_sync = start_frame[0]
end_sync = end_frame[-1]
bins_stim = np.concatenate((start_frame, end_frame[-1:]))

# Spikes
fspiketimes = h5py.File(sorting_file)
list_name = [kname for kname in fspiketimes['spiketimes']]
spiketimes = []
for key in list_name[:4]:
    timestamp = fspiketimes['/spiketimes/'+key][...]
    ts_checkerboard = sta.get_times_for_sta(timestamp, start_sync, end_sync)
    spiketimes.append((key, ts_checkerboard))
fspiketimes.close()


result = sta.run_multi_sta(stim_file, bins_stim, spiketimes,
                           pre_frame=nsamples_before, post_frame=nsamples_after)
print('Results (pool):\n', len(result))


if SAVA_FILE:
    import h5py
    filename = 'STAs_'+exp_name+'.hdf5'
    with h5py.File(filename, 'a') as hdf_file:
	    group_name = '/STA/'+intensity
	    for (key, ksta) in result:
	        unit_name = group_name+'/{}'.format(key)
	        hdf_file.create_dataset(unit_name, data=ksta, dtype=np.float, compression="gzip")
	    hdf_file[group_name].attrs['fps'] = fps
	    hdf_file[group_name].attrs['nsamples_before'] = nsamples_before
	    hdf_file[group_name].attrs['nsamples_after'] = nsamples_after
	    hdf_file[group_name].attrs['nsamples'] = nsamples_before+nsamples_after
	    hdf_file[group_name].attrs['time'] = (np.arange(-nsamples_before, nsamples_after)+1)/fps

