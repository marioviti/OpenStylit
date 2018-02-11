import numpy as np
from patchmatch_reversed import reversed_nnf_approx, reconstruction

def nnf_shape(A,B,patch_size):
    """
        compute nnf shape as (A.w,A.h) - patch_size//2*2
    """
    h,w = A.shape[0:2]
    h_nnf = h-patch_size//2*2
    w_nnf = w-patch_size//2*2
    return (h_nnf,w_nnf,3)

def uniform_step(A,B,inv_nnf,mask_B,real_nnf,patch_size):
    """
        for all source patches look for the best matching
        patch in the destination, once a destination patch
        has been assigned to its best match mask its location
        by setting its value to 0.0
    """
    w_map = np.zeros(B.shape[:2]) - 1.0
    max_d = np.max(inv_nnf[:,:,2])
    c = A.shape[2]
    h,w = inv_nnf.shape[:2]
    new_maskB = np.copy(mask_B)

    for i in range(h):
        for j in range(w):
            nnf_i,nnf_j,d =int(inv_nnf[i,j,0]),int(inv_nnf[i,j,1]),inv_nnf[i,j,2]
            # if the position is occupied go on
            if mask_B[nnf_i,nnf_j] == 0.0:
                continue
            if w_map[nnf_i,nnf_j] > d or w_map[nnf_i,nnf_j]<0.0:
                # if a new match or a better match is found
                # update the mask
                new_maskB[nnf_i,nnf_j] = 0.0
                w_map[nnf_i,nnf_j] = d
                real_nnf[nnf_i,nnf_j] = i,j,d

    mask_B[:,:] = new_maskB[:,:]
    return mask_B, w_map

def uniform(A,B,patch_size,
            mask_A = None,
            mask_B = None,
            real_nnf = None,
            inv_nnf = None,
            nnf_iterations=5,mu1=1.0,mu2=2.0,
            compesate_via_nnf=True):
    """
        A is the source and B is the target.
        Compute uniform patch match with reversed patch match
    """

    if mask_A is None:
        mask_A = np.ones(nnf_shape(A,B,patch_size)[:2])
    if mask_B is None:
        mask_B = np.ones(nnf_shape(B,A,patch_size)[:2])
    if real_nnf is None:
        real_nnf = np.zeros(nnf_shape(B,A,patch_size))
    if inv_nnf is None:
        inv_nnf = np.zeros(nnf_shape(A,B,patch_size))
    max_num_patch = float(np.sum(mask_B))
    done = False
    max_iter,i = 10,0
    pat_vals = [1.0]
    w_map = None
    while(not done and i<max_iter):

        # Computer reversed nnf
        inv_nnf = reversed_nnf_approx(A,B,inv_nnf,mask_A,mask_B,patch_size,nnf_iterations,mu1,mu2)
        # in uniforn_step assign source patches to target patches
        # mask each target patch with the best match
        mask_B,w_map = uniform_step(A,B,inv_nnf,mask_B,real_nnf,patch_size)

        # check for convergence
        used = np.sum(mask_B)
        percent = np.sum(mask_B)/max_num_patch
        done = percent < 0.05
        i+=1
        pat_vals += [percent]

    if pat_vals[-1]>0.0 and compesate_via_nnf:
        # retrive final patches by direct nnf
        final_nnf = np.zeros(nnf_shape(B,A,patch_size))
        mask_A = np.ones(nnf_shape(A,B,patch_size)[:2])
        final_nnf = reversed_nnf_approx(B,A,final_nnf,mask_B,mask_A,patch_size,nnf_iterations,0.0,mu2)
        real_nnf[mask_B==1.0]=final_nnf[mask_B==1.0]

    return w_map,inv_nnf,real_nnf,mask_B
