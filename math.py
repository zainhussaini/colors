import numpy as np

def seg_intersect(a1,a2, b1,b2):
    """Note: this function is really buggy"""
    da = a2-a1
    db = b2-b1
    dp = a1-b1

    def perp( a ) :
        b = np.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    return (num / denom.astype(float))*db + b1

a1 = np.array([0, 0])
a2 = np.array([1, 1])
b1 = np.array([3, 2])
b2 = np.array([5, 0])
res = seg_intersect(a1, a2, b1, b2)
print(res)
