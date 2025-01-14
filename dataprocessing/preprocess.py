from convert_to_scaled_off import to_off
from boundary_sampling import boundary_sampling
import voxelized_pointcloud_sampling as voxelized_pointcloud_sampling

from glob import glob
import multiprocessing as mp
from multiprocessing import Pool
import numpy as np

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import config_loader as cfg_loader

if __name__ == '__main__':
    cfg = cfg_loader.get_config()

    print('Finding raw files for preprocessing.')
    paths = glob(cfg.data_dir + cfg.input_data_glob)
    paths = sorted(paths)
    chunks = np.array_split(paths, cfg.num_chunks)
    paths = chunks[cfg.current_chunk]

    if cfg.num_cpus == -1:
        num_cpus = mp.cpu_count()
    else:
        num_cpus = cfg.num_cpus


    def multiprocess(func):
        p = Pool(num_cpus)
        p.map(func, paths)
        p.close()
        p.join()


    print('Start scaling.')
    multiprocess(to_off)

    print('Start distance field sampling.')
    for sigma in cfg.sample_std_dev:
        print(f'Start distance field sampling with sigma: {sigma}.')
        # multiprocess(partial(boundary_sampling, sigma = sigma))

        # this process is multi-processed for each path:
        # IGL parallelizes the distance field computation of multiple points.
        for path in paths:
            # print('path: {}'.format(path))
            boundary_sampling(path, sigma)

    print('Start voxelized pointcloud sampling.')
    voxelized_pointcloud_sampling.init(cfg)
    multiprocess(voxelized_pointcloud_sampling.voxelized_pointcloud_sampling)
