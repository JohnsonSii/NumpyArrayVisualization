import pickle

from sklearn.datasets import load_digits
digits = load_digits()
images = digits.images

print()
with open(r"./mnist.pkl", 'wb') as wf:
    pickle.dump(images, wf)
