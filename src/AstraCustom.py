import astra
import numpy as np
import matplotlib.pyplot as plt
from src.inline_scanning_setup import InlineScanningSetup
from math import sin, cos

def fanflat_simulation(dectors_numbers, matrix_data):

    vol_geom = astra.create_vol_geom(256, 256)
    proj_geom = astra.create_proj_geom('fanflat_vec', dectors_numbers, matrix_data)

    # As before, create a sinogram from a phantom
    import scipy.io
    P = scipy.io.loadmat('phantom.mat')['phantom256']
    proj_id = astra.create_projector('line_fanflat', proj_geom, vol_geom) #TODO: fix that, maybe in cuda works
    sinogram_id, sinogram = astra.create_sino(P, proj_id)

    import pylab
    pylab.gray()
    pylab.figure(1)
    pylab.imshow(P)
    pylab.figure(2)
    pylab.imshow(sinogram)

    # Create a data object for the reconstruction
    rec_id = astra.data2d.create('-vol', vol_geom)

    # create configuration
    cfg = astra.astra_dict('FBP')
    cfg['ReconstructionDataId'] = rec_id
    cfg['ProjectionDataId'] = sinogram_id
    cfg['ProjectorId'] = proj_id
    cfg['option'] = { 'FilterType': 'Ram-Lak' }

    # possible values for FilterType:
    # none, ram-lak, shepp-logan, cosine, hamming, hann, tukey, lanczos,
    # triangular, gaussian, barlett-hann, blackman, nuttall, blackman-harris,
    # blackman-nuttall, flat-top, kaiser, parzen


    # Create and run the algorithm object from the configuration structure
    alg_id = astra.algorithm.create(cfg)
    astra.algorithm.run(alg_id)

    # Get the result
    rec = astra.data2d.get(rec_id)
    pylab.figure(3)
    pylab.imshow(rec)
    pylab.show()

    # Clean up. Note that GPU memory is tied up in the algorithm object,
    # and main RAM in the data objects.
    astra.algorithm.delete(alg_id)
    astra.data2d.delete(rec_id)
    astra.data2d.delete(sinogram_id)
    astra.projector.delete(proj_id)


def create_matrix_fanflat(projection_angles, distance_origin_source, distance_origin_detector, detector_width):
    matrix = []
    # TODO: enviar a variação de angulo em radiano(?), enviar o array de distancias de cada um e a width do detector
    for i in range(len(projection_angles)):
        # source
        print(projection_angles[i])

        vector = []
        vector.append(sin(projection_angles[i]) * distance_origin_source[i])
        vector.append(-cos(projection_angles[i]) * distance_origin_source[i])

        # center of detector
        vector.append(-sin(projection_angles[i]) * distance_origin_detector[i])
        vector.append(cos(projection_angles[i]) * distance_origin_detector[i])

        # vector from detector pixel 0 to 1
        vector.append(cos(projection_angles[i]) * detector_width)
        vector.append(sin(projection_angles[i]) * detector_width)
        
        matrix.append(vector)
    matrix_np = np.array([[matrix[k][0], matrix[k][1], matrix[k][2], matrix[k][3], matrix[k][4],  matrix[k][5]] for k in range(len(matrix))])
    return matrix_np